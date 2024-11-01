# Environment
from dotenv import load_dotenv
import os

# for mongo 
from pymongo import MongoClient
from bson import ObjectId

# Data manipulation and storage
import pandas as pd

# Similarity and metrics
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# for glove
from gensim.models import KeyedVectors

#turning txt file into dataframe
def parse_article(text):
    lines= text.strip().split('\n')
    data= {}
    for line in lines:
        if ': ' in line: 
            key, value= line.split(': ',1)
            data[key.strip()]= value.strip()
    return data

def map_to_database_articles(df):
    load_dotenv()
    DATABASE_CONNECTION = os.getenv("DATABASE_CONNECTION")

    # MongoDB setup
    cluster = MongoClient(DATABASE_CONNECTION)
    db = cluster['llm-maritime-risk']
    collection_articles = db["Articles"]

    # Add columns for mapped data
    df["headline"] = ""
    df["description"] = ""
    df["severity"] = ""
    df["main_risk"] = ""
    df["country"] = ""
    df["state"] = ""
    df["link"] = ""

    indices_to_drop = []
    for i, id_value in enumerate(df['id']):
        mapped_document = collection_articles.find_one({"_id": ObjectId(id_value)})
        if mapped_document is None:
            indices_to_drop.append(i)
            continue
        elif "editorial" in mapped_document and mapped_document["editorial"]:
            indices_to_drop.append(i)
            continue
        df.at[i, "headline"] = mapped_document.get('headline', '')
        df.at[i, "description"] = mapped_document.get('description', '')
        df.at[i, "severity"] = mapped_document.get('severity', '')
        df.at[i, "main_risk"] = mapped_document.get('main_risk', '')
        df.at[i, "country"] = mapped_document.get('country', '')
        df.at[i, "state"] = mapped_document.get('state', '')
        df.at[i, "link"] = mapped_document.get('link', '')

    df = df.drop(index=indices_to_drop).reset_index(drop=True)
    return df

def create_dataframe(file_path):
    with open(file_path,'r', encoding="utf-8", errors="ignore") as f:
        articles= f.read().split('\n\n')
        
    data = [parse_article(article) for article in articles]
    df = pd.DataFrame(data).dropna()
    
    df['CombinedText'] = (df['Disruption event'].fillna('') + ' ' + df['Port Affected'].fillna('')).astype(str)

    return df

def combine_all_files(folder_path):
    combined_df = pd.DataFrame()
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):  # Check for text files
            file_path = os.path.join(folder_path, filename)
            df = create_dataframe(file_path)
            combined_df = pd.concat([combined_df, df], ignore_index=True)  # Concatenate the new DataFrame
    return combined_df

# standardising Ports Affected column
def standardize_port_affected(df):
    df['Port Affected'] = df['Port Affected'].replace(
        to_replace=[r'N/A', r'not', r'Not', r'None'],
        value=np.nan,
        regex=True
    )
    return df

# extracting from article
folder_path = 'summary_official_overall'
df = combine_all_files(folder_path)
df = standardize_port_affected(df)
df = map_to_database_articles(df)
#create sample
sample= df.sample(n=1000, random_state= 42).reset_index(drop=True)

glove_file = './glove.6B.300d.txt'  # Adjust path and dimensions as needed
glove_vectors = KeyedVectors.load_word2vec_format(glove_file, binary=False, no_header=True)

def deduplicate_articles(df, similarity_threshold=0.9):
    # Create a list to keep track of indices to drop
    indices_to_drop = set()
    
    # Iterate over each article and calculate similarity with others
    for i in range(len(df)):
        if i in indices_to_drop:
            continue  # Skip already marked articles
        
        vector_a = df['GloVe_Vectors'][i].reshape(1, -1)
        
        for j in range(i + 1, len(df)):
            vector_b = df['GloVe_Vectors'][j].reshape(1, -1)
            sim_score = cosine_similarity(vector_a, vector_b)
            
            if sim_score > similarity_threshold:
                indices_to_drop.add(j)  # Mark for removal if similarity exceeds threshold
    
    # Drop the marked indices and return the deduplicated DataFrame
    deduplicated_glove_df = df.drop(index=indices_to_drop).reset_index(drop=True)
    return deduplicated_glove_df

# Function to get the GloVe vector for a word or an average vector for a list of words
def vectorize_words(words):
    words = words.split()  # Split the text into words
    word_vectors = []
    
    for word in words:
        if word in glove_vectors:
            word_vectors.append(glove_vectors[word])
    
    if word_vectors:  # Return the average vector if any words are found
        return np.mean(word_vectors, axis=0)
    else:
        return np.zeros(glove_vectors.vector_size)  # Return a zero vector if no words are found

def get_glove_vectors(df):

    df['GloVe_Vectors'] = df['Disruption event'].apply(vectorize_words)
    return df

# # test on sample dataset
# glove_df = get_glove_vectors(sample)
# deduplicated_glove_df = deduplicate_articles(glove_df)
# deduplicated_glove_df.shape

glove_df = get_glove_vectors(df)
deduplicated_glove_df = deduplicate_articles(glove_df)
deduplicated_glove_df.shape

excel_file_path = 'output.xlsx'
deduplicated_glove_df.to_excel(excel_file_path, index=False)
print(f"DataFrame exported to {excel_file_path} successfully.")