import os
from dotenv import load_dotenv

# for mongo
from pymongo import MongoClient

# for preprocessing
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

# for summarising
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time

# setting up environment and global variables
load_dotenv()

cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
db = cluster['llm-maritime-risk']

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemma = WordNetLemmatizer()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def preprocess_words(text):
    if isinstance(text, str):
        words = text.split()
        filtered_words = ' '.join([word for word in words if word.lower() not in stop_words])
        normalized_words = ' '.join(lemma.lemmatize(word) for word in filtered_words.split())
        return normalized_words  
    return text

def filter_description(article):
    description = article['description']
    
    if 'gcaptain' in article['link']:
        description = description.split('(Reporting', 1)[0].strip()
        description = description.split('(Editing', 1)[0].strip()
        description = description.split('(reporting', 1)[0].strip()
        description = description.split('(editing', 1)[0].strip()
        description = description.split('Join the members that receive our newsletter', 1)[0].strip()
        description = description.split('Join the gCaptain', 1)[0].strip()
    elif 'loadstar' in article['link']:
        description = description.split('...', 1)[0]
        parts = description.split('.')
        if len(parts) > 1:
            description = '.'.join(parts[:-1]).strip()
    
    return description

def preprocess_article(article):
    description = filter_description(article)
    preprocessed_description = preprocess_words(description)

    headline = article.get("headline", "")
    preprocessed_headline = preprocess_words(headline)

    article["description"] = preprocessed_description
    article["headline"] = preprocessed_headline

    return article

def get_summary_and_data(article):
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
    time.sleep(5)
    return response

def parse_response(text):
    lines= text.strip().split('\n')
    data= {}
    for line in lines:
        if ': ' in line: 
            key, value= line.split(': ',1)
            data[key.strip()]= value.strip()
    return data

def map_articles_to_preprocessed_collection():
    scraped_articles_collection = db['Articles']
    processed_articles_collection = db['Processed_Articles']

    scraped_articles = scraped_articles_collection.find()
    processed_articles = processed_articles_collection.find()

    # for logs purpose
    expected_to_process = scraped_articles_collection.count_documents({}) - processed_articles_collection.count_documents({})
    print(f"Expected {expected_to_process} articles to process")
    counter = 1

    for article in scraped_articles:
        article_id = article.get("_id")
        is_processed = processed_articles_collection.find_one({"_id": article_id})
        if is_processed:
            continue

        processed_article = preprocess_article(article)

        response = get_summary_and_data(processed_article)
        response_results = parse_response(response.text)
        processed_article['summary'] = response_results.get('Disruption event', "")
        processed_article['extracted affected port'] = response_results.get("Port Affected", "")
        processed_article['extracted date'] = response_results.get("Date")

        processed_article['is new'] = True
        processed_article['is unique'] = True

        processed_articles_collection.insert_one(processed_article)
        if counter % 10 == 0:
            print(f"Processed {counter}/{expected_to_process} Articles!")
        if counter == 700:
            print("Exited because APIKey finishing")
            break
        counter += 1
    print("Finished!")

map_articles_to_preprocessed_collection()
