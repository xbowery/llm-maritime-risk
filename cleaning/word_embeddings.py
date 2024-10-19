# importing all necessary modules
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()
cluster = MongoClient({os.getenv("DATABASE_CONNECTION")})
db = cluster['llm-maritime-risk']
collection_articles = db["Articles"].find({})

deduplicated_collection = db["Deduplicated_Articles"]

# function to read the txt file and organise it
def get_documents():
    with open('../summarising/output/gemini/summary_official.txt', 'r') as file:
        content = file.read()

    blocks = content.split("id:")

    documents = []
    for block in blocks[1:]:
        id_match = re.search(r"\s*(\d+)", block)
        event_match = re.search(r"Disruption event:\s*(.*)", block)
        port_match = re.search(r"Port Affected:\s*(.*)", block)
        date_match = re.search(r"Date:\s*(.*)", block)

        if id_match and event_match and port_match and date_match:
            entry_id = id_match.group(1).strip()
            event = event_match.group(1).strip()
            port = port_match.group(1).strip()
            date = date_match.group(1).strip()

            # Create the dictionary in the desired format
            entry = {
                "id": entry_id,
                "event": event,
                "port affected": port,
                "date": date
            }

            documents.append(entry)
        else:
            print(block)
    return documents

def map_document_to_mapped_document(document, link, headline, description):
    document["link"] = link
    document["headline"] = headline
    document["description"] = description
    return document

def map_to_database(document):
    mapped_document = collection_articles.find_one({"id": document["id"]})
    if mapped_document == None:
        return None

    # ignore the mapping if it is an editorial article
    if mapped_document.get("is_editorial", False):
        return None
    new_document = map_document_to_mapped_document(document, mapped_document["link"], mapped_document["headline"], mapped_document["description"])
    return new_document

def tokenize(text):
    words = []
    for sentence in sent_tokenize(text):
        words.extend(word_tokenize(sentence))
    return [word.lower() for word in words]

def calculate_similarity(model, article_tokens, threshold=0.8):
    # Compute the average vector for the current article
    article_vector = np.mean([model.wv[token] for token in article_tokens if token in model.wv], axis=0)
    
    # If there are no valid tokens in the article, skip similarity check
    if article_vector is None or np.isnan(article_vector).any():
        return False
    
    # Compare the article vector with each existing word vector in the model
    for word in model.wv.index_to_key:
        existing_vector = model.wv[word].reshape(1, -1)
        article_vector = article_vector.reshape(1, -1)
        similarity = cosine_similarity(article_vector, existing_vector)[0][0]
        
        if similarity > threshold:
            return True  # Duplicate found
    
    return False  # No duplicate found

def add_article_to_model(model, article_tokens):
    # Update the model with the new article tokens
    model.build_vocab([article_tokens], update=True)
    model.train([article_tokens], total_examples=model.corpus_count, epochs=model.epochs)

def save_to_mongodb(article):
    # Insert the article into the collection
    deduplicated_collection.insert_one(article)

def deduplication_pipeline(articles, threshold=0.8):
    # Initialize the Word2Vec model
    model = Word2Vec(vector_size=100, window=5, min_count=1, workers=4)
    
    # Process each article
    for idx, article in enumerate(articles):
        if idx + 1 % 10 == 0:
            print(f"Processing article id: {article["_id"]} at {idx + 1}/{len(articles)}")
        
        mapped_article = map_to_database(article)
        if mapped_article == None:
            print(f"faced a problem at {article}")
            continue

        # Step 1: Tokenize the article
        article_tokens = tokenize(article["event"])
        
        # Step 2 & 3: Check if the article is a duplicate
        if model.wv:  # Check if the model already has some words
            if calculate_similarity(model, article_tokens, threshold):
                print(f"Article {mapped_article["_id"]} is a duplicate.")
                continue
        
        # Step 4: Add the article to the model
        add_article_to_model(model, article_tokens)
    
        # Step 5: Save the non-duplicate article to a separate MongoDB collection
        save_to_mongodb(article)

    print("Deduplication process complete.")

def main():
    articles = get_documents()
    deduplication_pipeline(articles, threshold=0.8)

if __name__ == "__main__":
    main()