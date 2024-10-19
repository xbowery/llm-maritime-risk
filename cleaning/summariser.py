from dotenv import load_dotenv
import os
from pymongo import MongoClient
import ollama

load_dotenv()

cluster = MongoClient({os.getenv("DATABASE_CONNECTION")})
db = cluster['llm-maritime-risk']
collection_articles = db["Articles"]
collection_cleaned = db["Summary"]
dataset = collection_articles.find({})
summarised = []

def query_article(prompt):
    response_dict = ollama.generate(
        model = 'gemma:2b',
        prompt = "Given the following article, provide a 100 word summary regarding ...\n\n" + prompt
    )
    response = response_dict['response']
    return response.lower()

# Process each article
for data in dataset:
    if 'editorial' in data and data['editorial']:
        continue

    summarised = query_article(data['description'])

# Save cleaned dataset back to MongoDB
print("Cleaned articles successfully!")