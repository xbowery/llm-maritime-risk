import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import pandas as pd
import time

os.makedirs('output/gemini', exist_ok=True)
load_dotenv()

cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
db = cluster['llm-maritime-risk']
collection = db["Articles"]
collection_articles = collection.find({"is_checked": False}).limit(500)


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
counter = 0

# Risk Identification
for article in collection_articles:
  if article['is_checked']:
    continue

  print(f"Reading article: {article['_id']}")
  # get the response from the model
  response = model.generate_content(f"""
  ## Your Role
  You are an Information Extractor & Summarization Expert. 
  This is extremely important as any the summary will provide insights into the events that cause port disruptions.

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
  """,
  safety_settings={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE
  })
  print(f"Saving article...") 

  with open('output/gemini/summary_official6.txt', 'a') as f:
    f.write(f"id: {article["_id"]}\n")
    f.write(response.text)
    f.write('\n\n')
    counter += 1

  new_field = {"is_checked": True}  
  result = collection.update_one(
      {"_id": article["_id"]},
      {"$set": new_field}
  )

  if counter % 10 == 0:
    print(f"Completed {counter} articles!")
    
  time.sleep(5)