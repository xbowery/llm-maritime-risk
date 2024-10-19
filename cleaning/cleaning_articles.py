from dotenv import load_dotenv
import os
from pymongo import MongoClient
import ollama
import utils

load_dotenv()

cluster = MongoClient({os.getenv("DATABASE_CONNECTION")})
db = cluster['llm-maritime-risk']
collection_articles = db["Articles"]
collection_cleaned = db["Cleaned_articles"]
dataset = collection_articles.find({})
cleaned = []

def query_article(prompt, expectedResponse):
    response_dict = ollama.generate(
        model = 'gemma:2b',
        prompt = prompt + "Provide your response as a Yes or No"
    )
    response = response_dict['response']
    if expectedResponse:
        return 'yes' in response.lower()
    return 'yes' not in response.lower()

def query_duplicate(article):
    user_prompt = f"Given the new article, determine if it is a duplicate from the provided dataset. Provide your response as a one-word response of either Yes or No, no need for explanations or reasons. \n\nnew article: {article}\nprovided dataset: {cleaned}"
    
    response_dict = ollama.generate(
         model='gemma:2b', 
        prompt = user_prompt
    )

    response = response_dict['response']
    return response

def isDuplicate(data):
        response = query_duplicate(data)
        return 'yes' in response.lower()

def isMaritime(data):
    count_is_maritime = 0
    prompt1 = f"Determine if the following article relates to maritime risks, hence causing disruptions:\n\n" \
             f"Headline: {data['headline']}\nContent: {data['description']}\n"
    if query_article(prompt1, True): count_is_maritime += 1
    prompt2 = f"- There are 4 main maritime risks: Port Strike, Port Disruption, Port Closure, and Port Congestion.\n"\
             f"As an experienced consultant specialized in maritime and international trading, determine if the following article relates to maritime risks and cause disruptions:\n\n"\
             f"Headline: {data['headline']}\nContent: {data['description']}\n"
    if query_article(prompt2, True): count_is_maritime += 1
    prompt3 = f"The following article discusses the risks linked to international maritime trade and factors causing disruption. Is this statement true?\n\n"\
             f"Headline: {data['headline']}\nContent: {data['description']}\n"
    if query_article(prompt3, True): count_is_maritime += 1
    
    return count_is_maritime >= 2  # Majority voting

# Process each article
for data in dataset:
    if 'is_checked' in data and data['is_checked']:
        cleaned.append(data)
        continue

    if not isMaritime(data):
        continue
    if isDuplicate(data):
        continue
    
    new_field = {"is_checked": True}  
    result = collection_articles.update_one(
        {"_id": data["_id"]},
        {"$set": new_field}
    )
    data.pop("_id", None)
    collection_cleaned.insert_one(data)
    cleaned.append(data)
    print(">>>processsed data<<<")

# Save cleaned dataset back to MongoDB
print("Cleaned articles successfully saved to MongoDB!")