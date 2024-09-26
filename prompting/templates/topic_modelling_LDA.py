from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

import pandas as pd


df = pd.read_excel('cleaned_risk data.xlsx')
des = df['Cleaned_Description'].to_list()


counter = 1
for text_sample in des:
    # Preprocessing and applying topic modeling (LDA)
    # Tokenizing the text, removing stop words, and fitting LDA model
    # Step 1: Convert text to a document-term matrix
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text_sample])

    # Step 2: Apply LDA to find topics
    lda = LatentDirichletAllocation(n_components=5, random_state=42)
    lda.fit(X)

    # Step 3: Displaying the topics with their top words
    words = vectorizer.get_feature_names_out()
    topics = {}
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [words[i] for i in topic.argsort()[:-6:-1]]  # Top 5 words per topic
        topics[f'Topic {topic_idx + 1}'] = top_words

    with open('..\\output\\topic_modelling\\topics.txt', 'a') as f:
        f.write(f'{counter}.\n')
        for topic, top_words in topics.items():
            f.write(f'{topic}: {", ".join(top_words)}\n')
        f.write('\n')

    counter += 1