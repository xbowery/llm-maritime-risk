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

documents = []
import re
with open('..\\output\\gemini\\summarisation3.txt', 'r') as file:
    lines = file.readlines()

pattern = r"\d+\.\s*Disruption event:\s*(.*)"

for i in range(0, len(lines), 5):
    match = re.search(pattern, lines[i])
    if match:
        disruption_event = match.group(1)
        documents.append(disruption_event)

# Create LSH index with threshold
lsh = MinHashLSH(threshold=0.1, num_perm=128)

# Add documents to LSH index
minhashes = {}  # Store MinHash signatures for later use
# read = set()
for i, doc in enumerate(documents):
    # if i >= 1000:
    #     break
    trigrams = get_trigrams(doc)
    m = minhash_signature(trigrams)
    # if doc['headline'] in read:
    #     print(f">>>> problem! {doc}")
    #     continue
    lsh.insert(f"{doc}", m)
    minhashes[f"{doc}"] = m  # Store the signature for comparison
    # read.add(doc)

# Querying for similar documents
for i, doc in enumerate(documents):
    query_doc = f"{doc}"
    query_trigrams = get_trigrams(query_doc)
    query_minhash = minhash_signature(query_trigrams)
    similar_docs = lsh.query(query_minhash)

    for doc_another in similar_docs:
        if doc_another == doc:
            continue
        sim_percentage = query_minhash.jaccard(minhashes[doc_another]) * 100
        print(f"Document 1'{doc}' and Document 2 '{doc_another}': {sim_percentage:.2f}%")