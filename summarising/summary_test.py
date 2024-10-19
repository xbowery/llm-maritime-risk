import google.generativeai as genai
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import pandas as pd
import time

os.makedirs('..\\output\\gemini', exist_ok=True)
load_dotenv()

cluster = MongoClient({os.getenv("DATABASE_CONNECTION")})
db = cluster['llm-maritime-risk']
collection_articles = db["Articles"].find({
  "headline":
    {'$regex': "Francis Scott Key Bridge"}
})
cleaned = []


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
counter = 1

# Risk Identification given 3 choices, last choice as Port Disruption.
for article in collection_articles:
   response = model.generate_content(f"""
    ## Your Role
    You are an Information Extractor & Summarization Expert.

    ## Your Task
    Given the following headline and content, provide:

        The disruption event that happened in 30 words or less.
        The name of the affected port.
        The date mentioned.
        Use the exact format:
        Disruption event:
        Port Affected:
        Date:

        Headline: '{article["headline"]}'
        Content: '{article["description"]}'
    """)
   with open('..\\output\\gemini\\summarisation3.txt', 'a') as f:
      f.write(str(counter) + '. ')
      f.write(response.text)
      f.write('\n\n')
      counter += 1
   time.sleep(5)