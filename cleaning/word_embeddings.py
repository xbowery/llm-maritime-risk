# importing all necessary modules
from gensim.models import Word2Vec
import gensim
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import re
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize


warnings.filterwarnings(action='ignore')


with open('..\\output\\gemini\\summarisation3.txt', 'r') as file:
    lines = file.readlines()

pattern = r"\d+\.\s*Disruption event:\s*(.*)"

documents = []
for i in range(0, len(lines), 5):
    match = re.search(pattern, lines[i])
    if match:
        disruption_event = match.group(1)
        documents.append(disruption_event)

data = []

# iterate through each sentence in the file
for document in documents:
    sentences = sent_tokenize(document)  # Split document into sentences
    for sentence in sentences:
        words = word_tokenize(sentence)   # Tokenize sentence into words
        words = [w.lower() for w in words]  # Lowercase the words
        data.append(words)

# Create CBOW model
model = gensim.models.Word2Vec(data, min_count=1,
								vector_size=100, window=5)

# Function to get document vector (average of word vectors)
def document_vector(doc, model):
    words = word_tokenize(doc.lower())  # Tokenize the document
    words = [word for word in words if word in model.wv.key_to_index]  # Filter out words not in vocab
    if words:
        return np.mean(model.wv[words], axis=0)  # Return average word vectors
    else:
        return np.zeros(model.vector_size)  # Return zero vector if no words in vocab

# Calculate document vectors
doc_vectors = [document_vector(doc, model) for doc in documents]

# Check similarity between documents using cosine similarity
similarity_matrix = cosine_similarity(doc_vectors)

# Set a similarity threshold
threshold = 0.7

# Compare documents and check if they are similar above the threshold
for i in range(len(documents)):
    for j in range(i + 1, len(documents)):
        similarity = similarity_matrix[i][j]
        if similarity > threshold:
            print(f"Document {i+1} and Document {j+1} are similar with a similarity score of {similarity:.2f}")

