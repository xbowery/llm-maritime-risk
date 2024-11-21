### README: GloVe-Based Article Deduplication

This script leverages GloVe word vectors to perform article deduplication by comparing articles' vector representations. Articles are deemed to be duplicates if they have a similarity score above the threshold of 0.9 (equivalent to 90%)

---

### Setup

To run this script, you need to 

1. **GloVe Vectors**: Download the pre-trained GloVe word vectors. Take note that the file size is `822MB`! You may download the `glove.6B.300d.txt` file from the [GloVe website](https://nlp.stanford.edu/projects/glove/). Store the file in the `cleaning` subdirectory

2. **Dependencies**: Install the necessary Python libraries:

```
pip install -r requirements.txt
```

### Functionality

#### Loading the Vectors
This step utilises the pre-trained GloVe vectors provided within the downloaded file. The script will read the word embeddings into a dictionary, where the key is the word and the value is the corresponding word vector.

After which, articles which have been deduplicated before will be maintained, and their GloVe vectors will be obtained through mapping against the GloVe vectors previously stored into a dictionary.

#### Deduplication
For the new articles, their GloVe vectors will also be obtained through mapping against the GloVe Vectors previously stored into a dictionary. However it will then be checked against the deduplicated articles for duplication, by calculating the cosine similarity with other vectors. 

After which, the database flag `is new` is set to `False` as it has been processed. If the new article is deemed to be a duplication, the `is unique` flag is also set to `False`.

### Configuration

In the script, you may need to configure the following:

- **DATABASE_CONNECTION**: Set up the environment variable for the MongoDB instance. 

---

### Running the Code
You may run the code after configurating the above keys. Ensure that you are in the `cleaning` sub directory.
```
python deduplicate.py
```
