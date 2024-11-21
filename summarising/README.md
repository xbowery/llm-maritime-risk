### README: Article Summarizer and Processing Pipeline

This script processes news articles that were scraped by first preprocessing the description and headline. Next, the processed data is passed through the `Gemini-1.5-flash` Large Language Model (LLM) using prompt engineering to extract relevant information. The extracted data, including summary and affected ports, is stored in the `Processed_Articles` database. The database will contain fields corresponding to the processed description, headline, and additional fields generated from the LLM output. Each article will also have flags to indicate whether it is new and unique that is stored.

---

### Setup

To run this script, you need to install the necessary Python libraries:

```
pip install -r requirements.txt
```

### Functionality

#### Preprocessing

The preprocessing step involves cleaning the headline and description of articles. The goal is to:

- Remove irrelevant characters (e.g., extra spaces, HTML tags, special characters).
- Standardize text formatting (e.g., lowercasing).
- Tokenize and prepare the text for LLM input.

#### LLM Data Extraction

Once the data is preprocessed, we pass both the description and headline through a language model using **prompt engineering**. This step generates:

- **Summary**: The disruption event that happened in 30 words or less.
- **Port Affected**: The name of the affected port.
- **Date**: The date mentioned.

The prompt is carefully crafted to instruct the LLM to extract these specific data points from the article text.

#### Database Insertion

After extracting the data, the following fields are inserted into the `Processed_Articles` MongoDB collection:

1. **Headline**: The processed headline.
2. **Description**: The processed description.
3. **Extracted Fields**: Fields like summary, port affected, and any other data extracted via the LLM.
4. **Flags**:
   - `is new`: Indicates if the article is new (default to `True`).
   - `is unique`: Indicates whether the article is unique, based on deduplication logic (default to `True`).

---

### Configuration

In the script, you may need to configure the following:

- **DATABASE_CONNECTION**: Set up the environment variable for the MongoDB instance. 
  
- **GEMINI_API_KEY**: Set up the environment variable for the `Gemini-1.5-flash` model. Currently the scripts limit the calls at 700 per run so as to avoid exceeding the limit of the Free Tier.

---

### Running the Code
You may run the code after configurating the above keys. Ensure that you are in the `summarising` sub directory.
```
python summarize.py
```