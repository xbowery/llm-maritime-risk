from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

import pandas as pd

# Load the data
df = pd.read_excel('cleaned_risk data.xlsx')
des = df['Cleaned_Description'].to_list()

counter = 1

for i in des:
    doc = sent_tokenize(i)

    tokenized_words = [word_tokenize(sentence) for sentence in doc]

    # Remove stop words
    cleaned_token = [[word for word in sentence if word.isalpha()] for sentence in tokenized_words]

    # create a dictionary
    dictionary = Dictionary(cleaned_token)

    # Create a corpus from the document
    corpus = [dictionary.doc2bow(text) for text in cleaned_token]

    model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, random_state=42)

    with open('..\\output\\topic_modelling\\topics1.txt', 'a') as f:
        f.write(f'{counter}.\n')
        for topic in model.show_topics(formatted=False):
            words = [word[0] for word in topic[1]]
            f.write(", ".join(words))
            f.write('\n')
        f.write('\n')

    counter += 1