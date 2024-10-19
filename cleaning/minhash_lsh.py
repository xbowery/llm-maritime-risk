import re
from datasketch import MinHash, MinHashLSH
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Helper function to get trigrams from text
def get_trigrams(text):
    text = re.sub(r'\W+', '', text.lower())  # Remove non-alphanumeric characters and lowercase the text
    return [text[i:i+3] for i in range(len(text) - 2)]

# Generate MinHash signature
def minhash_signature(trigrams, num_perm=128):
    m = MinHash(num_perm=num_perm)
    for trigram in trigrams:
        m.update(trigram.encode('utf8'))
    return m

load_dotenv()

cluster = MongoClient({os.getenv("DATABASE_CONNECTION")})
db = cluster['llm-maritime-risk']
collection_articles = db["Articles"]
collection_cleaned = db["Cleaned_articles"]
dataset = collection_articles.find({})
documents = []
for data in dataset:
    if 'editorial' in data and not data['editorial']:
        documents.append(data)
        continue

# Create LSH index with threshold
lsh = MinHashLSH(threshold=0.5, num_perm=128)

# Add documents to LSH index
minhashes = {}  # Store MinHash signatures for later use
read = set()
for i, doc in enumerate(documents):
    # if i >= 1000:
    #     break
    trigrams = get_trigrams(doc['description'])
    m = minhash_signature(trigrams)
    if doc['headline'] in read:
        print(f">>>> problem! {doc['headline']}")
        continue
    lsh.insert(f"{doc['headline']}", m)
    minhashes[f"{doc['headline']}"] = m  # Store the signature for comparison
    read.add(doc['headline'])

# Querying for similar documents
duplicated = set()
for i, doc in enumerate(documents):
    if doc['headline'] in duplicated:
        continue
    query_doc = f"{doc['description']}"
    query_trigrams = get_trigrams(query_doc)
    query_minhash = minhash_signature(query_trigrams)
    similar_docs = lsh.query(query_minhash)

    for doc_headline in similar_docs:
        if doc_headline == doc['headline']:
            continue
        sim_percentage = query_minhash.jaccard(minhashes[doc_headline]) * 100
        print(f"Similarity between '{doc['headline']}' and '{doc_headline}': {sim_percentage:.2f}%")
        duplicated.add(doc_headline)

