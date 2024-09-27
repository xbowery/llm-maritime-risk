import os
import pandas as pd
import time
from mistralai import Mistral
from dotenv import load_dotenv

df = pd.read_excel('cleaned_risk data.xlsx')
des = df['Cleaned_Description']

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "open-mistral-7b"

client = Mistral(api_key=api_key)

def classify_risk(description):
    prompt = f"""Given the following text: 

    {description}

    ## Your Role
    You are a consultant specialized in maritime and international trading. You must accurately classify the type of port risk based on collected newspaper articles.
    This is extremely important as any inaccurate classification can lead to a loss of over a million dollars due to suboptimal route planning. 

    ## Your Task
    - There are 4 main risks: Port Strike, Port Disruption, Port Closure, and Port Congestion. Print what you know about the difference between the different risks.
    - Based on the articles given, think step by step and provide the final risk classification.
    - You must give a risk classification.
    - After giving your final answer, think: are you sure of it? Reflect on it and provide a new answer if you are unsure.

    Output only the final risk classification. An example of your answer should be: Port Disruption.
    """
    
    chat_response = client.chat.complete(
        model= model,
        messages = [
            {
                "role": "user",
                "content": f"{prompt}",
            },
        ]
    )

    return chat_response.choices[0].message.content

counter = 1

for i in des:
    try:
        result = classify_risk(i)
        
        with open('..\\output\\mistral\\prompt_and_cleaned\\risk_identification.txt', 'a') as f:
            f.write(str(counter) + '. ')
            f.write(result)
            f.write('\n\n')
        
        counter += 1
        
        time.sleep(5)
        
    except Exception as e:
        print(f"Error on description {counter}: {e}")
        with open('..\\output\\mistral\\prompt_and_cleaned\\risk_identification.txt', 'a') as f:
            f.write(str(counter) + '. ')
            f.write("Error occurred")
            f.write('\n\n')
        counter += 1