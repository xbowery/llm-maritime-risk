from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

cluster = MongoClient({os.getenv("DATABASE_CONNECTION")})
db = cluster['llm-maritime-risk']
collection = db["Articles"]

class Article:
    def __init__(self, headline, description, severity, main_risk, country, state):
        self.headline = headline
        self.description = description
        self.severity = severity
        self.main_risk = main_risk
        self.country = country
        self.state = state

    def to_dict(self):
        return {
            "headline": self.headline,
            "description": self.description,
            "severity": self.severity,
            "main_risk": self.main_risk,
            "country": self.country,
            "state": self.state
        }
    

##################################
# Example Code
##################################

news_article = Article(
    "Headline_value",
    "Description_value",
    "Severity rating",
    "Main_risk type",
    "Country affected",
    "State affected"
)

collection.insert_one(news_article.to_dict())

