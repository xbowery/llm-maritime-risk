
"""
MongoDB Probability Matrix Generator
This script connects to MongoDB cluster, fetches classification and severity data,
and generates a probability matrix with visualizations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pprint import pprint

def setup_mongodb():
    """Setup MongoDB cluster connection"""
    load_dotenv()
    cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
    db = cluster['llm-maritime-risk']
    collection = db['Processed_Articles']
    return cluster, collection

def fetch_data_from_mongodb(collection):
    """Fetch data from MongoDB and convert to DataFrame"""
    try:
        # Fetch all documents from the collection
        cursor = collection.find(
            {},  # Empty query to fetch all documents
            {
                'Final Classification': 1, 
                'predicted_severity': 1,
                '_id': 0  # Exclude _id field
            }
        )
        
        # Convert cursor to DataFrame
        df = pd.DataFrame(list(cursor))
        
        if df.empty:
            raise ValueError("No data found in the specified collection")
            
        return df
        
    except Exception as e:
        raise Exception(f"Error fetching data from MongoDB: {str(e)}")

def create_probability_matrix(df):
    """Create and display probability matrix from DataFrame"""
    # Create a cross-tabulation of Final Classification and predicted severity
    prob_matrix = pd.crosstab(df['Final Classification'], 
                             df['predicted_severity'],
                             normalize='index',  # normalize by rows
                             margins=True)  # add row and column totals
    
    # Convert to percentages
    prob_matrix = prob_matrix.multiply(100).round(1)
    
    # Create a heatmap
    plt.figure(figsize=(15, 10))
    
    # Create heatmap without the 'All' row and column
    heatmap_data = prob_matrix.iloc[:-1, :-1]
    
    # Create heatmap
    sns.heatmap(heatmap_data, 
                annot=True, 
                fmt='.1f', 
                cmap='Blues',
                cbar_kws={'label': 'Percentage (%)'})
    
    plt.title('Probability Matrix: Final Classification vs Predicted Severity')
    plt.xlabel('Predicted Severity Level')
    plt.ylabel('Final Classification')
    plt.tight_layout()
    plt.show()
    
    # Print detailed analysis
    print("\nDetailed Probability Breakdown:")
    print("=" * 80)
    print("\nProbability Matrix (%):")
    print(prob_matrix)
    
    # Calculate total number of articles for each classification
    total_counts = df['Final Classification'].value_counts()
    print("\nTotal Articles per Classification:")
    print("=" * 80)
    for classification, count in total_counts.items():
        print(f"{classification}: {count} articles")
    
    # Find dominant severity levels for each classification
    print("\nDominant Severity Levels per Classification:")
    print("=" * 80)
    for classification in heatmap_data.index:
        row = heatmap_data.loc[classification]
        dominant_severity = row.idxmax()
        dominant_percentage = row.max()
        print(f"{classification}:")
        print(f"  Most common severity: Level {dominant_severity} ({dominant_percentage:.1f}%)")

def main():
    try:
        # Setup MongoDB connection
        cluster, collection = setup_mongodb()
        
        # Print sample documents for verification
        print("\nVerifying connection - Sample documents (first 3):")
        for doc in collection.find().limit(3):
            pprint(doc)
            
        # Fetch data from MongoDB
        df = fetch_data_from_mongodb(collection)
        
        # Create probability matrix
        create_probability_matrix(df)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nPlease ensure:")
        print("1. MongoDB connection string is properly set in environment variables")
        print("2. Collection contains 'Final Classification' and 'predicted_severity' fields")
    
    finally:
        # Close MongoDB connection
        if 'cluster' in locals():
            cluster.close()

if __name__ == "__main__":
    main()