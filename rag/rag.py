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
    
    def generate_category(
        self,
        texts: List[str],
        filter_others: bool = True
    ) -> str:
        """
        Generate a risk category description from similar texts using OpenAI.
        
        Args:
            texts: List of text strings to categorize
            filter_others: Whether to exclude common categories
            
        Returns:
            Generated risk category name
        """
        combined_text = " ".join(texts)
        example_categories = [
            "Vessel Delay", "Vessel Accidents", "Piracy", "Route Congestion",
            "Port Criminal Activity", "Cargo Damage and Loss",
            "Inland Transportation Risk", "Environmental Impact and Pollution",
            "Extreme Weather", "Cargo Detainment"
        ]
        
        prompt_template = """
        You are a maritime risk analysis assistant. Below is a list of common maritime risk categories{exclusion}:
        {categories}
        
        Based on the recent maritime incidents described here:
        "{incidents}"
        
        Generate the most suitable risk category for these incidents.{instruction} Please provide only a single category.
        
        Risk Category:
        """
        
        exclusion = " (do NOT use any of these)" if filter_others else ""
        instruction = (
            " Do NOT use any of the listed categories. Instead, create a unique risk category."
            if filter_others else
            " Use one of the listed categories if it fits, or create a new one if needed."
        )
        
        prompt = prompt_template.format(
            exclusion=exclusion,
            categories=", ".join(example_categories),
            incidents=combined_text,
            instruction=instruction
        )
        
        response = self.client.chat.completions.create(
            model=self.generator_model,
            messages=[
                {"role": "system", "content": "You are a specialized assistant in maritime risk analysis, providing concise and accurate risk categories."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
    
    def discover_risk_categories(
        self,
        data: pd.DataFrame,
        k_range: range = range(2, 10),
        method: str = 'silhouette',
        filter_others: bool = False,
        samples_per_cluster: int = 30
    ) -> Tuple[List[Dict[str, Union[str, List[str], int]]], np.ndarray]:
        """
        Discover risk categories from texts using clustering and RAG.
        
        Args:
            data: DataFrame containing disruption events
            k_range: Range of cluster numbers to try
            method: Clustering method ('elbow', 'silhouette', or 'both')
            filter_others: Whether to analyze only "Others" category
            samples_per_cluster: Number of samples to use per cluster for category generation
            
        Returns:
            Tuple of (categories list, cluster assignments)
        """
        if filter_others:
            data = data[data['Final Classification'] == "Others"]
            if len(data) == 0:
                raise EmptyDataFrameError(
                    "No articles with 'Others' category found in the provided data."
                )
        texts = data['Disruption event'].tolist()
        
        if self.index is None:
            self.build_index(texts)
        
        embeddings = self.encode_texts(texts)
        optimal_k, _ = self._find_optimal_k(embeddings, k_range, method)
        
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        
        categories = []
        for i in range(optimal_k):
            cluster_texts = [
                text for text, cluster in zip(texts, clusters)
                if cluster == i
            ]
            
            if not cluster_texts:
                continue
                
            n = min(samples_per_cluster, len(cluster_texts))
            sampled_texts = cluster_texts[:n]
            
            categories.append({
                'category': self.generate_category(sampled_texts, filter_others),
                'sample_texts': sampled_texts,
                'size': len(cluster_texts)
            })
            
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
        filename = 'data_new.xlsx'
        try:
            data = pd.read_excel(filename, index_col=0)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            exit(1)
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            exit(1)

        # Discover risk categories
        print('Running the Pipeline')
        try:
            categories, clusters = rag.discover_risk_categories(
                data,
                k_range=range(2, 10),
                method='silhouette',
                filter_others=True
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

        # Export data
        try:
            data_copy = data.copy()
            data_copy.loc[data_copy['Final Classification'] == 'Others', 'Final Classification'] = list(map(lambda x: cluster_names[x], clusters))
            data_copy.to_excel('data_new_categories.xlsx')
            print(f'Data exported to data_new_categories.xlsx!')
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            exit(1)
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        exit(1)