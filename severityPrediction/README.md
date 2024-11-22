# Maritime Risk Classification

A comprehensive system for analyzing and classifying maritime risk incidents using advanced AI models. This solution compares zero-shot classification and Google's Gemini AI to provide detailed risk severity assessments.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Gemini API:
```bash
# Create .env file and add your API key
echo "GEMINI_API_KEY=your_key_here" > .env
```

3. Run the analysis:
```bash
python severity_predictions.py
```

## How It Works

The system analyzes maritime incidents through three main components:

### 1. Zero-Shot Classification
- Utilizes pre-trained language models for initial risk assessment
- Applies industry-standard severity categories
- Provides rapid classification without training data

### 2. Gemini AI Analysis
- Deep analysis of incident descriptions
- Context-aware severity assessment
- Advanced natural language understanding

### 3. Severity Assessment
- 5-level classification system
- Comprehensive risk impact evaluation
- Comparative analysis of classification methods

## Data Requirements

### Input Format
- Headline in text format
- Description of the article
- Risk Type 


### Output Format
- Severity classifications from both models
- Confidence scores
- Comparative analysis results

## Configuration Options

### Model Settings
```python
classifier = MaritimeRiskClassifier(
    zero_shot_model="cross-encoder/nli-distilroberta-base",
    gemini_model="gemini-pro"
)
```

### Classification Parameters
```python
results = classifier.analyze_incidents(
    data=incidents,
    confidence_threshold=0.6,    # Minimum confidence score
    include_reasoning=True       # Include model reasoning
)
```

## Error Handling

The system includes robust error handling for:
- Invalid API credentials
- Malformed input data
- Model availability issues
- Classification failures

Example error messages:
```
Error: Invalid Gemini API key
Error: Input data missing required fields
Error: Classification confidence below threshold
```

## Technical Details

### Dependencies
Required libraries:
- `torch`: Deep learning framework
- `transformers`: Zero-shot classification
- `google-generativeai`: Gemini AI integration
- `pandas`: Data management
- `matplotlib`: Visualization
- `tqdm`: Progress tracking

### System Requirements
- Python 3.9 or higher
- Active Gemini API key
- Sufficient computational resources

## Limitations and Considerations

- Classification accuracy depends on:
  - Quality of incident descriptions
  - Context availability
  - Model confidence scores
- Processing time varies with:
  - Dataset size
  - Analysis depth
  - API response times

## Example Usage

```python
# Initialize classifier
classifier = MaritimeRiskClassifier()

# Load and process data
incidents = pd.read_csv('maritime_incidents.csv')
results = classifier.analyze_incidents(incidents)

# View results
print(results.summary())

# Export classifications
results.to_excel('risk_classifications.xlsx')
```

## Results Analysis

### Distribution Comparison

Zero-Shot Classifier:
- Low: 0.8%
- Moderate: 59.9%
- High: 19.4%
- Critical: 3.1%
- Catastrophic: 16.8%

Gemini Model:
- Low: 18.9%
- Moderate: 33.6%
- High: 26.7%
- Critical: 18.0%
- Catastrophic: 2.7%

## Future Enhancements

- Enhanced prompt engineering
- Integration of additional risk factors
- Improved model comparison metrics
- Development of hybrid prediction systems




---
<div align="center">
Advancing maritime safety through intelligent risk analysis
</div>