# imports
import os
from dotenv import load_dotenv

# for mongo
from pymongo import MongoClient

# for summarising
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
import re

#setup global variables
load_dotenv()

cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
db = cluster['llm-maritime-risk']

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def get_category(article, new=False):
    prompt_template = """Given the following text{s}:                                       
{article}

## Your Role
You are a consultant specialized in maritime and international trading. 
This is extremely important because any inaccurate classification or lack of details can lead to a loss of over a million dollars due to suboptimal route planning.

## Your Task
- These are the categories and descriptions of maritime risks{exclusion}:
{categories}
- Based on the article{s} given, think step by step and provide{instruction}.
- You must give a single final risk classification.
- After giving your final answer, think: are you sure of it? Reflect on it and provide your final answer.

Output only the final classification{description}.
"""
    
    # Prompt formatting
    categories = [
        f"\t- {category['Category']}: {category['Description']}" 
        for category in list(db['Risk_Categories'].find())
    ] # Get existing risk categories
    if new:
        s = "s"
        exclusion = " (do NOT use any of these)"
        articles = "- " + "\n- ".join(article)
        instruction = ' a single unique and concise risk classification that best describes these articles. Follow the format of the existing categories provided earlier. Do NOT use the word "maritime" in your classification'
        description = " and the corresponding short description separated by a colon"
    else:
        s = ""
        exclusion = ""
        articles = article['summary']
        instruction = " the final risk classification"
        description = ""

    prompt = prompt_template.format(
        s=s,
        exclusion=exclusion,
        categories="\n".join(categories),
        article=articles,
        instruction=instruction,
        description=description
    )
    
    response = model.generate_content(
        prompt,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, 
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE
        },
    )
    time.sleep(5)
    return response

def parse_response(text):
    text = text.strip().split('\n')[0]
    cleaned_text = re.sub(r'[^A-Za-z0-9\s:]', '', text)
    return cleaned_text

def update_database(article):
    processed_articles_collection = db['Processed_Articles']

    processed_articles_collection.update_one(
        {"_id": article['_id']},
        {"$set": {
            'main_risk': article['main_risk'],
            'final_risk': article['main_risk']
        }}
    )

def generate_category():
    processed_articles_collection = db['Processed_Articles']
    empty_category_articles = processed_articles_collection.find({"main_risk": "", "is unique": True})

    # for logs purpose
    expected_to_process = processed_articles_collection.count_documents({"main_risk": "", "is unique": True})
    print(f"Expected {expected_to_process} articles to process")
    counter = 1

    for article in empty_category_articles:

        response = get_category(article)
        article['main_risk'] = parse_response(response.text)

        update_database(article)
        if counter % 10 == 0:
            print(f"Processed {counter}/{expected_to_process} Articles!")
        if counter == 700:
            print("Exited because APIKey finishing")
            break
        counter += 1

if __name__ == "__main__":
    generate_category()