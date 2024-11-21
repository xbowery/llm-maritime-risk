# imports
import os
from dotenv import load_dotenv

# for mongo
from pymongo import MongoClient

# for preprocessing
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

# for deduplication
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import KeyedVectors


## set up global variables
load_dotenv()

cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
db = cluster['llm-maritime-risk']

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemma = WordNetLemmatizer()

glove_file = './glove.6B.300d.txt'
glove_vectors = KeyedVectors.load_word2vec_format(glove_file, binary=False, no_header=True)

def preprocess_words(text):
    if isinstance(text, str):
        words = text.split()
        filtered_words = ' '.join([word for word in words if word.lower() not in stop_words])
        normalized_words = ' '.join(lemma.lemmatize(word) for word in filtered_words.split())
        return normalized_words  
    return text

def preprocess_article(article):
    summary = article.get("summary", "")
    preprocessed_summary = preprocess_words(summary)

    article["summary"] = preprocessed_summary
    return article

def vectorize_words(words):
    words = words.split()
    word_vectors = []
    
    for word in words:
        if word in glove_vectors:
            word_vectors.append(glove_vectors[word])
    
    if word_vectors:
        return np.mean(word_vectors, axis=0)
    else:
        return np.zeros(glove_vectors.vector_size)
    
def determine_is_duplicate(deduplicated_df, given_article, similarity_threshold=0.9):
    vector_given = given_article['glove vector'].reshape(1, -1)
    for _, orig_article in deduplicated_df.iterrows():
        vector_existing = orig_article['glove vector'].reshape(1, -1)
        similarity_score = cosine_similarity(vector_given, vector_existing)
        
        if similarity_score > similarity_threshold:
            return True
    
    return False

def update_database(article):
    processed_articles_collection = db['Processed_Articles']

    processed_articles_collection.update_one(
        {"_id": article['_id']},
        {"$set": {'is new': article['is new'],
                  'is unique': article['is unique'],
                  'summary': article['summary']
                  }}
    )

def process_articles():
    processed_articles = db['Processed_Articles'].find({})
    df = pd.DataFrame(processed_articles)

    deduplicated_articles = pd.DataFrame(columns=df.columns)
    if not df[~df['is new'] & df['is unique']].empty:
        deduplicated_articles = df[~df['is new'] & df['is unique']]
    deduplicated_articles['glove vector'] = deduplicated_articles['summary'].apply(vectorize_words)
    
    new_articles = df[df['is new']]
    # new_articles = deduplicated_articles

    # for logs
    expected_to_process = len(new_articles)
    print(f"Expected to process {expected_to_process} Articles")
    counter = 1

    for _, given_article in new_articles.iterrows():
        given_article = preprocess_article(given_article)
        given_article_vector = vectorize_words(given_article['summary'])
        given_article['glove vector'] = given_article_vector

        is_duplicate = determine_is_duplicate(deduplicated_articles, given_article)
        given_article['is new'] = False
        if is_duplicate:
            given_article['is unique'] = False
        else:
            given_article_df = pd.DataFrame([given_article])
            deduplicated_articles = pd.concat([deduplicated_articles, given_article_df], ignore_index=True)

        update_database(given_article)

        if counter % 10 == 0:
            print(f"Processed {counter}/{expected_to_process} Articles!")
        if counter == 700:
            print(f"Exited because 700 Articles processed")
            break
        counter += 1

    print(f"Finished processing!")

process_articles()