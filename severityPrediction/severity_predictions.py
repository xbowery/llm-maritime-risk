# imports
import os
from dotenv import load_dotenv
import time
from tqdm import tqdm


# for mongo
from pymongo import MongoClient

# for models
import google.generativeai as genai
import torch
from transformers import pipeline

## set up global variables
load_dotenv()

cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
db = cluster['llm-maritime-risk']

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

class MaritimeRiskClassifier:
    def __init__(self, model_name: str = "cross-encoder/nli-distilroberta-base"):
        # Initialize Zero-Shot Classifier
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_name,
            device=0 if torch.cuda.is_available() else -1
        )

        # Severity levels for classification
        self.severity_levels = {
            1: "Low Severity - Minor impact, no injuries, minor cleanup.",
            2: "Moderate Severity - Noticeable impact, non-critical injuries, moderate cleanup.",
            3: "High Severity - Substantial impact, critical injuries, or multi-hour disruptions.",
            4: "Critical Severity - Severe incident, major injuries, significant cleanup.",
            5: "Catastrophic Severity - Extreme impact, fatalities, severe long-term consequences."
        }
        self.candidate_labels = list(self.severity_levels.values())

        # Gemini Prompt
        self.few_shot_prompt = """
            You are a maritime severity assessor. 
            Based on the headline, description, risk type, and affected port of each maritime incident, 
            assign a severity level (1-5) by considering the following criteria:

            - Human Impact: The extent of injuries or fatalities.
            - Environmental Impact: Spills, pollution, or ecosystem damage.
            - Operational Disruption: Delays, rerouting, or other operational impacts.
            - Potential for Escalation: Risk of worsening, like fire or further environmental harm.

            Severity levels:
            - **1 (Low Severity)**: Minor impact, no injuries, minor cleanup.
            - **2 (Moderate Severity)**: Noticeable impact, non-critical injuries, moderate cleanup.
            - **3 (High Severity)**: Substantial impact, critical injuries, or multi-hour disruptions.
            - **4 (Critical Severity)**: Severe incident, major injuries, significant cleanup.
            - **5 (Catastrophic Severity)**: Extreme impact, fatalities, severe long-term consequences.

            Respond with only the severity level as a single number (1, 2, 3, 4, or 5).
            """
        
    def predict_zero_shot(self, headline, description, main_risk):
        """Predict severity using Zero-Shot Classifier."""
        headline = self.clean_input(headline)
        description = self.clean_input(description)
        main_risk = self.clean_input(main_risk)
        text = f"{headline} | {main_risk} | {description[:200]}"
        if not text.strip():
            return {"severity_level": 1, "severity_label": "Low Severity", "confidence": 0.0}

        result = self.classifier(text, self.candidate_labels)
        predicted_label = result['labels'][0]
        confidence = result['scores'][0]
        severity_level = self._get_severity_level(predicted_label)
        return {"severity_level": severity_level, "severity_label": predicted_label, "confidence": confidence}
    
    def predict_gemini(self, headline, description, main_risk, extracted_affected_port):
        """Predict severity using Gemini model."""
        input_prompt = (
            f"{self.few_shot_prompt}\n"
            f"**Headline**: {headline}\n"
            f"**Description**: {description}\n"
            f"**Main Risk**: {main_risk}\n"
            f"**Affected Port**: {extracted_affected_port}\n"
            "Assessment: Severity Level:"
        )
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(input_prompt)
        time.sleep(5)
        severity_level = response.candidates[0].text.strip()
        return {"severity_level": int(severity_level), "severity_label": severity_level}
    
    def _get_severity_level(self, label):
        """Map severity label to numerical level."""
        severity_mapping = {l.split(' -')[0]: i for i, l in self.severity_levels.items()}
        return severity_mapping.get(label.split(' -')[0], 1)
    
    def classify_severity_articles(self, use_model="zero-shot"):
        """Process articles using the specified model (zero-shot or gemini)."""
        articles_collection = db['Processed_Articles']
        articles = list(articles_collection.find({"is_unique": True}))

        for article in tqdm(articles, desc="Processing Articles"):
            headline = article.get("headline", "")
            description = article.get("description", "")
            main_risk = article.get("main_risk", "")
            extracted_affected_port = article.get("extracted affected port", "")

            if use_model == "zero-shot":
                prediction = self.predict_zero_shot(headline, description, main_risk)
            elif use_model == "gemini":
                prediction = self.predict_gemini(headline, description, main_risk, extracted_affected_port)
            else:
                raise ValueError("Invalid model choice. Use 'zero-shot' or 'gemini'.")

            # Update article with severity and severity label
            articles_collection.update_one(
                {"_id": article["_id"]},
                {"$set": {
                    "severity": prediction["severity_level"],
                    "severity_label": prediction["severity_label"]
                }}
            )

        print(f"Finished processing {len(articles)} articles!")



classifier = MaritimeRiskClassifier()
# Use 'zero-shot' or 'gemini' to specify the model for predictions
classifier.classify_severity_articles(use_model="zero-shot")


