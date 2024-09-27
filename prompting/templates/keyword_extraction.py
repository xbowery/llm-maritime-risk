from keybert import KeyBERT

import pandas as pd


df = pd.read_excel('cleaned_risk data.xlsx')
des = df['Cleaned_Description'].to_list()

counter = 1

kw_model = KeyBERT('distilbert-base-nli-mean-tokens')
for i in des:
    keywords = kw_model.extract_keywords(i, keyphrase_ngram_range=(1,2), top_n=10)

    with open('..\\output\\keyword_extraction\\keywords.txt', 'a') as f:
        f.write(str(counter) + '. ')
        for word in keywords:
            f.write(f'{word[0]}, ')
        f.write('\n\n')

    counter += 1