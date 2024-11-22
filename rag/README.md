# Maritime Risk RAG System

A powerful tool for analyzing and categorizing maritime risk incidents using artificial intelligence. The system combines advanced text analysis with OpenAI's language models to automatically identify and classify maritime disruption events.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up OpenAI API:
```bash
# Create .env file and add your API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

3. Run the analysis:
```bash
python rag.py
```

## How It Works

The system processes maritime incident data through three main stages:

### 1. Text Analysis
- Converts incident descriptions into mathematical representations (embeddings)
- Builds a searchable index for finding similar incidents

### 2. Pattern Discovery
- Groups similar incidents using clustering techinque
- Identifies common patterns in maritime risks
- Automatically determines optimal number of risk categories

### 3. Category Generation
- Creates meaningful category names using OpenAI's GPT models
- Considers industry-standard maritime risk categories
- Can generate new categories for unique or unusual incidents

## Data Requirements

### Input Format
- File: `data_new.xlsx`
- Required columns:
  - `Disruption event`: Description of the incident
  - `Final Classification`: Current category of the incident
  
Example:
```
| Disruption event                      | Final Classification |
|---------------------------------------|---------------------|
| Port closed due to severe weather     | Weather Related     |
| Cargo vessel delayed by equipment...  | Others              |
```

### Output Format
- File: `data_new_categories.xlsx`
- Contains all original data
- Updated classifications for previously uncategorized ("Others") incidents

## Configuration Options

### Model Settings
```python
rag = MaritimeRiskRAG(
    encoder_model="sentence-transformers/all-mpnet-base-v2",  # For text analysis
    generator_model="gpt-4o-mini"                            # For category generation
)
```

### Analysis Parameters
```python
categories, clusters = rag.discover_risk_categories(
    data=data,
    k_range=range(2, 10),    # Number of categories to consider
    method='silhouette',     # Method for choosing optimal categories
    filter_others=True       # Focus on uncategorized incidents
)
```

## Error Handling

The system includes comprehensive error checks for:
- Missing or invalid input files
- Empty datasets after filtering
- Invalid configuration parameters
- API authentication issues
- Data processing errors

Example error messages:
```
Error: No articles with 'Others' category found in the provided data.
Error: Invalid method 'invalid_method'. Must be one of: 'elbow', 'silhouette', 'both'
Error: File 'data_new.xlsx' not found.
```

## Technical Details

### Dependencies
Core libraries used:
- `sentence-transformers`: Text analysis
- `faiss-cpu`: Similarity search
- `pandas`: Data handling
- `scikit-learn`: Machine learning
- `openai`: Category generation
- `python-dotenv`: Configuration

### System Requirements
- Python 3.7 or higher
- Active OpenAI API key
- Sufficient memory for dataset processing

## Limitations and Considerations

- Processing time scales with dataset size
- OpenAI API rate limits may apply
- Quality of categorization depends on:
  - Data quality
  - Dataset size
  - Incident description clarity

## Example Usage

```python
# Initialize system
rag = MaritimeRiskRAG()

# Load and process data
data = pd.read_excel('data_new.xlsx')
categories, clusters = rag.discover_risk_categories(data)

# View results
results_df = format_risk_analysis(categories)
print(results_df)

# Export categorized data
data_copy = data.copy()
data_copy.loc[data_copy['Final Classification'] == 'Others', 'Final Classification'] = \
    [results_df['Category'][x] for x in clusters]
data_copy.to_excel('data_new_categories.xlsx')
```