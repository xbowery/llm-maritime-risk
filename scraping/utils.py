from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re

class Article:
    def __init__(self, headline, description, severity, main_risk, country, state, link):
        self.headline = headline
        self.description = description
        self.severity = severity
        self.main_risk = main_risk
        self.country = country
        self.state = state
        self.link = link

    def to_dict(self):
        return {
            "_id": self.link,
            "headline": self.headline,
            "description": self.description,
            "severity": self.severity,
            "main_risk": self.main_risk,
            "country": self.country,
            "state": self.state,
            "link": self.link
        }

# Establish a MongoDB connection
def get_mongodb_collection():
    load_dotenv()
    cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
    db = cluster['llm-maritime-risk']
    collection = db["Articles"]
    return collection

def get_testing_mongodb_collection():
    load_dotenv()
    cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
    db = cluster['llm-maritime-risk']
    collection = db["Testing"]
    return collection

# Clean and normalize scraped text
def clean_text(text: str) -> str:
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'[\r\n\t]+', ' ', text)      # Remove newlines and tabs
    text = re.sub(r'\s+', ' ', text).strip()    # Collapse multiple spaces and trim
    return text
