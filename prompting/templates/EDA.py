import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

# Load the Excel file
file_path = '240902_Sample risk data SMU.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemma = WordNetLemmatizer()

def preprocess_words(text):
    if isinstance(text, str):  # Ensure the text is a string
        words = text.split()  # Split the text into words
        filtered_words = ' '.join([word for word in words if word.lower() not in stop_words]) # remove stopwords
        normalized_words = ' '.join(lemma.lemmatize(word) for word in filtered_words.split()) #lemmatize each word
        return normalized_words  
    return text  # Return unchanged if not a string

df['Cleaned_Headline'] = df['Headline'].apply(preprocess_words)
df['Cleaned_Description'] = df['Description'].apply(preprocess_words)

# Display the updated DataFrame
print(df[['Headline', 'Cleaned_Headline']].head())
print(df[['Description', 'Cleaned_Description']].head())

#Save cleaned data
df.to_excel('cleaned_risk data.xlsx', index=False) 