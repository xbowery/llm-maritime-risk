# Import necessary modules
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import logging
from typing import List, Dict, Any
from bson import ObjectId
from datasketch import MinHash, MinHashLSH

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DATABASE_CONNECTION = os.getenv("DATABASE_CONNECTION")

# MongoDB setup
cluster = MongoClient(DATABASE_CONNECTION)
db = cluster['llm-maritime-risk']
collection_articles = db["Articles"]
deduplicated_collection = db["Deduplicated_Articles_Minhash"]

# Function to read the txt file and organize it
def get_documents(filename: str) -> List[Dict[str, str]]:
    with open(filename, 'r', errors='replace') as file:
        content = file.read()

    print(f"Processing file: %s\n", filename)

    counter = 0
    blocks = content.split("id:")
    documents = []

    for block in blocks[1:]:
        entry = extract_document(block)
        if entry:
            documents.append(entry)
        else:
            print(f"Failed to extract document from block")
        counter += 1
        if counter % 100 == 0:
            print(f"Processing document: %d/%d\n", counter, len(blocks) - 1)
    
    return documents

def extract_document(block: str) -> Dict[str, str]:
    """Extract a document's details from a given block of text."""
    id_match = re.search(r"(\S+)", block)  # Capture the ID (non-whitespace characters)
    event_match = re.search(r"Disruption event:\s*(.*?)(?=Port Affected:|$)", block, re.DOTALL)
    port_match = re.search(r"Port Affected:\s*(.*?)(?=Date:|$)", block, re.DOTALL)
    date_match = re.search(r"Date:\s*(.*)", block)

    # If ID is found
    if id_match and event_match and port_match and date_match:
        return {
            "_id": id_match.group(1).strip(),
            "event": event_match.group(1).strip(),
            "port_affected": port_match.group(1).strip(),
            "date": date_match.group(1).strip()
        }

    return None

def map_document_to_mapped_document(document: Dict[str, str], link: str, headline: str, description: str) -> Dict[str, Any]:
    document["link"] = link
    document["headline"] = headline
    document["description"] = description
    return document

def map_to_database(document: Dict[str, str]) -> Dict[str, Any]:
    """Fetch and map the article details from the database."""
    mapped_document = db['Articles'].find_one({"_id": ObjectId(document["_id"])})
    if mapped_document is None:
        print(f"Faced a problem because None, {document['_id']}")
        return None
    elif "is_editorial" in mapped_document and mapped_document["is_editorial"]:
        print(f"Faced a problem at {document["_id"]} is editorial")
        return None
    elif "is_deduplicated" in mapped_document and mapped_document["is_deduplicated"]:
        print(f"Faced a problem at {document["_id"]} is duplicated")
        return None
    return map_document_to_mapped_document(document, mapped_document["link"], mapped_document["headline"], mapped_document["description"])

def save_to_mongodb(article) -> None:
    """Insert deduplicated article and update the original collection."""
    try:
        article_id = article["_id"]
        if isinstance(article_id, str):
            article_id = ObjectId(article_id)

        deduplicate_article_object = {
            "headline": article.get('headline', ''),
            "description": article.get('description', ''),
            "severity": article.get('severity', ''), 
            "main_risk": article.get('main_risk', ''),
            "country": article.get('country', ''), 
            "state": article.get('state', ''), 
            "link": article.get('link', ''),  # Default value
            "_id": article_id,
            "event": article.get('event', ''),
            "port_affected": article.get('port_affected', ''),
            "date": article.get('date', '')
        }

        deduplicated_collection.insert_one(deduplicate_article_object)

        # Update the original collection
        update_result = collection_articles.update_one(
            {"_id": article_id},
            {"$set": {"is_deduplicated": True}}
        )
    except Exception as e:
        print(f"Error in save_to_mongodb: {e}")

# Helper function to get trigrams from text
def get_trigrams(text):
    text = re.sub(r'\W+', '', text.lower())
    return [text[i:i+3] for i in range(len(text) - 2)]

# Generate MinHash signature
def minhash_signature(trigrams, num_perm=128):
    m = MinHash(num_perm=num_perm)
    for trigram in trigrams:
        m.update(trigram.encode('utf8'))
    return m

def check_similarity(query_article, lsh, minhashes, threshold = 0.9):
    query_doc = f"{query_article['_id']}"
    query_trigrams = get_trigrams(query_doc)
    query_minhash = minhash_signature(query_trigrams)
    similar_articles = lsh.query(query_minhash)

    for similar_article in similar_articles:
        sim_percentage = query_minhash.jaccard(minhashes[similar_article]) * 100
        if sim_percentage >= threshold:
            return True
    return False

def deduplication_pipeline(articles, threshold=0.9):
    lsh = MinHashLSH(threshold=0.1, num_perm=128)
    minhashes = {}
    for i, article in enumerate(articles):
        query_article = map_to_database(article)
        if query_article is None:
            continue
        
        # check if similar to existing articles
        is_duplicate = check_similarity(query_article, lsh, minhashes, threshold)
        if is_duplicate:
            continue

        trigrams = get_trigrams(query_article['event'])
        m = minhash_signature(trigrams)
        lsh.insert(f"{query_article['_id']}", m)
        minhashes[f"{query_article['_id']}"] = m

        # Step 5: Save the non-duplicate article to a separate MongoDB collection
        save_to_mongodb(query_article)  # Save immediately after processing

        if i % 100 == 0:
            print(f"Completed {i} articles")

    print("Deduplication process complete.")

def main() -> None:
    """Main function to execute the deduplication pipeline."""
    articles = []
    articles.extend(get_documents('../summarising/output/gemini/summary_official.txt'))
    
    for i in range(2, 15):
        articles.extend(get_documents(f'../summarising/output/gemini/summary_official{i}.txt'))

    deduplication_pipeline(articles, threshold=0.9)

if __name__ == "__main__":
    main()
