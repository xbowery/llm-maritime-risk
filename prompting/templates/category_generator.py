# imports
import os
from dotenv import load_dotenv

# for mongo
from pymongo import MongoClient

# for summarising
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time

#setup global variables
load_dotenv()

cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
db = cluster['llm-maritime-risk']

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def get_category(article):
    output = list(db['Risk_Categories'].find())

    categories = ""
    for category in output:
        categories += f"\t- {category['Category']}: {category['Description']}\n"

    response = model.generate_content(f"""Given the following text: 
                                      
    {article['summary']}

    ## Your Role
    You are a consultant specialized in maritime and international trading. 
    This is extremely important because any inaccurate classification or lack of details can lead to a loss of over a million dollars due to suboptimal route planning.
    ## Your Task
    - These are the categories of risks:
    {categories}
    - Based on the article given, think step by step and provide the final risk classification.
    - You must give a single final risk classification.
    - After giving your final answer, think: are you sure of it? Reflect on it and provide a new answer if you are unsure.

    Output only the final classification.
    """,
    safety_settings={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE
    })
    time.sleep(5)
    return response

def parse_response(text):
    lines= text.strip().split('\n')
    return lines[0]

def update_database(article):
    processed_articles_collection = db['Processed_Articles']

    processed_articles_collection.update_one(
        {"_id": article['_id']},
        {"$set": {'main_risk': article['main_risk']
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

generate_category()