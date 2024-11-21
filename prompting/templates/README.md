### README: Category Generation using LLM

This script processes the summaries of the articles to generate a risk category for each of the events. Specifically, these categories will fall within the 13 categories as provided to us. This is done through the use of prompt engineering and the `Gemini-1.5-flash` Large Language Model (LLM) that extracts the information and maps to a category. This method was tested against a sample database and then evaluated to be the most suitable in providing the Risk Category of the article.

---

### Setup

To run this script, you need to install the necessary Python libraries:

```
pip install -r requirements.txt
```

### Functionality

#### LLM Data Extraction

Once the data is preprocessed, we pass both the description and headline through a language model using **prompt engineering**. This step generates:

- Final Risk Category value

The prompt is carefully crafted to instruct the LLM to extract these specific data points from the article text.

#### Database Insertion

After extracting the data, the following fields are inserted into the `Processed_Articles` MongoDB collection:

1. `main_risk`: the Risk Category of the article as evaluated by the LLM

---
### Configuration

In the script, you may need to configure the following:

- **DATABASE_CONNECTION**: Set up the environment variable for the MongoDB instance. 

- **GEMINI_API_KEY**: Set up the environment variable for the `Gemini-1.5-flash` model. Currently the scripts limit the calls at 700 per run so as to avoid exceeding the limit of the Free Tier.
---

### Running the Code
You may run the code after configurating the above keys. Ensure that you are in the `prompting/templates` sub directory.
```
python category_generator.py
```
