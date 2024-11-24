import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pprint import pprint
import certifi

def setup_mongodb():
    """Setup MongoDB cluster connection with proper SSL verification"""
    load_dotenv()
    cluster = MongoClient(
        os.getenv("DATABASE_CONNECTION"),
        tlsCAFile=certifi.where()
    )
    db = cluster['llm-maritime-risk']
    collection = db['Processed_Articles']
    return cluster, collection

def fetch_data_from_mongodb(collection):
    """Fetch data from MongoDB and convert to DataFrame"""
    try:
        # Fetch all documents from the collection with the correct field names
        cursor = collection.find(
            {},  # Empty query to fetch all documents
            {
                'main_risk': 1,  # Changed from 'Final Classification'
                'severity': 1,   # Changed from 'predicted_severity'
                '_id': 0
            }
        )
        
        # Convert cursor to DataFrame with renamed columns
        df = pd.DataFrame(list(cursor))
        
        if df.empty:
            raise ValueError("No data found in the specified collection")
        
        # Rename columns to match the expected format
        df = df.rename(columns={
            'main_risk': 'Risk Type',
            'severity': 'Severity Level'
        })
            
        return df
        
    except Exception as e:
        raise Exception(f"Error fetching data from MongoDB: {str(e)}")

def create_probability_matrix(df):
    """Create and display probability matrix from DataFrame"""
    # Create a cross-tabulation of Risk Type and Severity Level
    prob_matrix = pd.crosstab(df['Risk Type'], 
                             df['Severity Level'],
                             normalize='index',
                             margins=True)
    
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
    
    plt.title('Risk Type vs Severity Level Distribution')
    plt.xlabel('Severity Level')
    plt.ylabel('Risk Type')
    plt.tight_layout()
    plt.show()
    
    # Print detailed analysis
    print("\nDetailed Probability Breakdown:")
    print("=" * 80)
    print("\nProbability Matrix (%):")
    print(prob_matrix)
    
    # Calculate total number of articles for each risk type
    total_counts = df['Risk Type'].value_counts()
    print("\nTotal Articles per Risk Type:")
    print("=" * 80)
    for risk_type, count in total_counts.items():
        print(f"{risk_type}: {count} articles")
    
    # Find dominant severity levels for each risk type
    print("\nDominant Severity Levels per Risk Type:")
    print("=" * 80)
    for risk_type in heatmap_data.index:
        row = heatmap_data.loc[risk_type]
        dominant_severity = row.idxmax()
        dominant_percentage = row.max()
        print(f"{risk_type}:")
        print(f"  Most common severity: Level {dominant_severity} ({dominant_percentage:.1f}%)")

def main():
    try:
        # Setup MongoDB connection
        cluster, collection = setup_mongodb()
        
        # Print collection info first
        print("\nChecking database connection and collection contents:")
        total_docs = collection.count_documents({})
        print(f"Total documents in collection: {total_docs}")
        
        # Fetch data from MongoDB
        df = fetch_data_from_mongodb(collection)
        
        # Create probability matrix
        create_probability_matrix(df)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTroubleshooting guide:")
        print("1. Ensure MongoDB connection string is correct in .env file")
        print("2. Check if documents contain the required fields:")
        print("   - 'main_risk'")
        print("   - 'severity'")
    
    finally:
        # Close MongoDB connection
        if 'cluster' in locals():
            cluster.close()

if __name__ == "__main__":
    main()