# LLM Prompting Setup
This guide walks you through setting up the environment for using the LLM APIs to prompt. It includes steps to create and activate a virtual environment, install dependencies, and set up the Jupyter kernel for interactive development.

## Step 1: Install Dependencies
Navigate to the scraping folder from the project's root directory.
```bash
cd prompting
```

The required dependencies are installed from the `requirements.txt` file when setting up the environment.
```bash
pip install -r requirements.txt
```

## Step 2: Fill in the API keys
Ensure the API keys are generated and copied to your `.env` file.

## Step 3: Run the files
For Google Gemini (Gemini-1.5-Flash):
```bash
python gemini_gen.py
```

For OpenAI (GPT-4o):
```bash
python openai_gen.py
```

For Mistral:
```bash
python mistral_gen.py
```

## Running the pipeline
Please run `store_categories.py` first to store all categories into the database, followed by `extract_categories.py`.