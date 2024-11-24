from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
import faiss
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from kneed import KneeLocator
from openai import OpenAI
from collections import Counter
import dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo import UpdateOne
from dotenv import load_dotenv
import os
import pandas as pd
import sys

# setting path to import from sibling directory
sys.path.append('..')
from prompting.templates.category_generator import get_category, parse_response

load_dotenv()

class EmptyDataFrameError(Exception):
    """Raised when the DataFrame after filtering is empty."""
    pass

class InvalidMethodError(Exception):
    """Raised when an invalid clustering method is specified."""
    pass

class MaritimeRiskRAG:
    """
    A RAG (Retrieval-Augmented Generation) system for maritime risk analysis.
    
    This class provides functionality to analyze maritime incidents, categorize risks,
    and discover patterns in maritime risk data using embedding-based retrieval and 
    OpenAI's language models for generation.
    """
    
    def __init__(
        self,
        encoder_model: str = "sentence-transformers/all-mpnet-base-v2",
        generator_model: str = "gpt-4o-mini"
    ):
        """
        Initialize the Maritime Risk RAG system.
        
        Args:
            encoder_model: Name or path of the sentence transformer model for text encoding
            generator_model: Name of the OpenAI model for text generation
        """
        self.encoder = SentenceTransformer(encoder_model)
        
        # Initialize OpenAI client
        self.generator_model = generator_model
        self.client = OpenAI(api_key=dotenv.get_key('.env', 'OPENAI_API_KEY'))
        
        # Initialize FAISS index and texts storage
        self.index: Optional[faiss.IndexFlatL2] = None
        self.texts: Optional[List[str]] = None
        
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode a list of texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            numpy.ndarray: Array of text embeddings
        """
        return self.encoder.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
    
    def build_index(self, texts: List[str]) -> None:
        """
        Build a FAISS index from text embeddings for similarity search.
        
        Args:
            texts: List of text strings to index
        """
        self.texts = texts
        embeddings = self.encode_texts(texts)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
    def retrieve_similar(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Union[str, float, int]]]:
        """
        Retrieve similar texts for a given query.
        
        Args:
            query: Text string to find similar documents for
            k: Number of similar documents to retrieve
            
        Returns:
            List of dictionaries containing similar texts, distances, and indices
        """
        if self.index is None or self.texts is None:
            raise ValueError("Index not built. Call build_index() first.")
            
        query_embedding = self.encode_texts([query])
        distances, indices = self.index.search(
            query_embedding.astype('float32'),
            k
        )
        
        return [
            {
                'text': self.texts[idx],
                'distance': float(distance),
                'index': int(idx)
            }
            for distance, idx in zip(distances[0], indices[0])
        ]
    
    def update_database_categories(
        self,
        db: Database,
        original_data: pd.DataFrame,
        clusters: np.ndarray,
        cluster_names: List[str]
    ) -> None:
        """
        Update the final_risk column in the database with newly discovered risk categories.
        
        Args:
            db: MongoDB database connection
            original_data: Original DataFrame containing the articles
            clusters: Cluster assignments for each article
            cluster_names: Names of the discovered clusters/categories
        """
        # Get indices of articles with 'Others' category
        others_mask = original_data['main_risk'] == 'Others'
        others_indices = original_data[others_mask].index
        
        # Create a mapping of document IDs to new categories
        updates = []
        for idx, cluster_idx in zip(others_indices, clusters):
            doc_id = original_data.loc[idx, '_id']
            new_category = cluster_names[cluster_idx]
            
            updates.append(UpdateOne(
                {'_id': doc_id},
                {'$set': {'final_risk': new_category}}
            ))
            
        # Perform bulk update
        if updates:
            result = db['Processed_Articles'].bulk_write(updates)
            print(f"Updated {result.modified_count} documents in the database")
    
    def generate_category(
        self,
        texts: List[str],
    ) -> str:
        response = get_category(texts, new=True)
        response = parse_response(response.text)
        category, description = response.split(': ')

        return category, description
    
    def discover_risk_categories(
        self,
        data: pd.DataFrame,
        db: Database,
        k_range: range = range(2, 10),
        method: str = 'silhouette',
        samples_per_cluster: int = 20,
        minimum_samples: int = 500
    ) -> Tuple[List[Dict[str, Union[str, List[str], int]]], np.ndarray]:
        """
        Discover risk categories from texts using clustering and RAG.
        
        Args:
            data: DataFrame containing disruption events
            k_range: Range of cluster numbers to try
            method: Clustering method ('elbow', 'silhouette', or 'both')
            samples_per_cluster: Number of samples to use per cluster for category generation
            
        Returns:
            Tuple of (categories list, cluster assignments)
        """
        data = data[data['main_risk'] == "Others"]
        if len(data) < minimum_samples:
            raise EmptyDataFrameError(
                f"minimum_samples is currently set to {minimum_samples} while there are only {len(data)} articles categorized as 'Others'. You can reduce the 'minimum_samples' parameter if you still want to proceed."
            )
        texts = data['summary'].tolist()
        
        if self.index is None:
            self.build_index(texts)
        
        embeddings = self.encode_texts(texts)
        optimal_k, _ = self._find_optimal_k(embeddings, k_range, method)
        
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        
        categories = []

        print('Generating risk categories..')
        for i in range(optimal_k):
            cluster_texts = [
                text for text, cluster in zip(texts, clusters)
                if cluster == i
            ]
            
            if not cluster_texts:
                continue
                
            n = min(samples_per_cluster, len(cluster_texts))
            sampled_texts = cluster_texts[:n]
            
            category, desc = self.generate_category(sampled_texts)
            categories.append({
                'category': category,
                'sample_texts': sampled_texts,
                'size': len(cluster_texts),
                'description': desc
            })
            
            # Insert new category to db
            document = {
                "Category": category,
                "Description": desc
            }
            db['Risk_Categories'].insert_one(document)
        
        return categories, clusters

    def _find_optimal_k(
        self,
        embeddings: np.ndarray,
        k_range: range,
        method: str
    ) -> Tuple[int, Dict[str, Union[List[int], List[float], int]]]:
        """
        Find optimal number of clusters using elbow method and/or silhouette analysis.
        
        Args:
            embeddings: Document embeddings
            k_range: Range of k values to try
            method: One of 'elbow', 'silhouette', or 'both'
            
        Returns:
            Tuple of (optimal k, metrics dictionary)
        """

        if method not in ['elbow', 'silhouette', 'both']:
            raise InvalidMethodError(
                f"Invalid method '{method}'. Must be one of: 'elbow', 'silhouette', 'both'"
            )
        
        inertias = []
        silhouette_scores = []
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(embeddings)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(
                silhouette_score(embeddings, kmeans.labels_)
                if k > 2 else 0
            )
                
        elbow_k = KneeLocator(
            list(k_range),
            inertias,
            curve='convex',
            direction='decreasing'
        ).knee
        
        best_silhouette_k = k_range[np.argmax(silhouette_scores)]
        
        metrics = {
            'k_range': list(k_range),
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'elbow_k': elbow_k,
            'best_silhouette_k': best_silhouette_k
        }
        
        if method == 'elbow':
            optimal_k = elbow_k
        elif method == 'silhouette':
            optimal_k = best_silhouette_k
        else:  # both
            optimal_k = round((elbow_k + best_silhouette_k) / 2)
        
        print(f'{optimal_k} clusters found!')
        return optimal_k, metrics

def format_risk_analysis(
    categories: List[Dict[str, Union[str, List[str], int]]]
) -> pd.DataFrame:
    """
    Format risk categories into a DataFrame.
    
    Args:
        categories: List of category dictionaries with category name, sample texts, and size
        
    Returns:
        DataFrame containing formatted risk analysis
    """
    return pd.DataFrame([
        {
            'Category': cat['category'],
            'Number of Incidents': cat['size'],
            'Example Incidents': '\n'.join(cat['sample_texts'][:3])
        }
        for cat in categories
    ])

if __name__ == '__main__':
    try:
        # Initialize RAG system
        print('Initializing the RAG Pipeline..')
        rag = MaritimeRiskRAG()
        
        # Load the data
        print('Loading the Data..')
        try:
            cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
            db = cluster['llm-maritime-risk']
            collection = db["Processed_Articles"]
            data = pd.DataFrame(list(collection.find({})))
            size = collection.count_documents({})
            print(f'{size} articles loaded!')
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            exit(1)

        # Discover risk categories
        print('Running the Pipeline..')
        try:
            categories, clusters = rag.discover_risk_categories(
                data,
                db,
                k_range=range(2, 10),
                method='silhouette',
            )
        except EmptyDataFrameError as e:
            print(f"Error: {str(e)}")
            exit(1)
        except InvalidMethodError as e:
            print(f"Error: {str(e)}")
            exit(1)
        except Exception as e:
            print(f"Error during risk category discovery: {str(e)}")
            exit(1)

        # Format and display results
        print("Formatting Results..")
        results_df = format_risk_analysis(categories)
        cluster_names = results_df['Category'].tolist()
        classes = list(map(lambda x: cluster_names[x], clusters))
        counts = Counter(classes)
        print(counts)

        # Update the database with new categories
        print("Updating database with new categories...")
        try:
            rag.update_database_categories(db, data, clusters, cluster_names)
            print("Database update completed successfully!")
        except Exception as e:
            print(f"Error updating database: {str(e)}")
            exit(1)

        # Export data
        # try:
        #     data_copy = data.copy()
        #     data_copy.loc[data_copy['main_risk'] == 'Others', 'main_risk'] = list(map(lambda x: cluster_names[x], clusters))
        #     data_copy.to_excel('data_new_categories.xlsx')
        #     print(f'Data exported to data_new_categories.xlsx!')
        # except Exception as e:
        #     print(f"Error exporting data: {str(e)}")
        #     exit(1)
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        exit(1)