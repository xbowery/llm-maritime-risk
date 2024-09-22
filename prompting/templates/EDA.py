import pandas as pd
import nltk
from nltk.corpus import stopwords

# Load the Excel file
file_path = '240902_Sample risk data SMU.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def remove_stop_words(text):
    if isinstance(text, str):  # Ensure the text is a string
        words = text.split()  # Split the text into words
        filtered_words = [word for word in words if word.lower() not in stop_words]
        return ' '.join(filtered_words)  # Join words back into a string
    return text  # Return unchanged if not a string

df['Cleaned_Headline'] = df['Headline'].apply(remove_stop_words)
df['Cleaned_Description'] = df['Description'].apply(remove_stop_words)

# Display the updated DataFrame
print(df[['Headline', 'Cleaned_Headline']].head())
print(df[['Description', 'Cleaned_Description']].head())

#Save cleaned data
df.to_excel('cleaned_risk data.xlsx', index=False) 