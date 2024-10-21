from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import time

load_dotenv()

df = pd.read_excel('cleaned_risk data.xlsx')
des = df['Cleaned_Description']

client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        organization=os.environ.get("OPENAI_ORG")
    )

counter = 1

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

    Output only the final classification."""
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "system", "content": ''},
            {"role": "user", "content": f'{prompt}'},
        ],
    )
    
    return response.choices[0].message.content

for i in des:
    try:
        result = classify_risk(i)
        
        with open('openai_risk_identification.txt', 'a') as f:
            f.write(str(counter) + '. ')
            f.write(result)
            f.write('\n\n')
        
        counter += 1
        
        time.sleep(5)
        
    except Exception as e:
        print(f"Error on description {counter}: {e}")
        with open('..\\output\\enhanced_choice_risks.txt', 'a') as f:
            f.write(str(counter) + '. ')
            f.write("Error occurred")
            f.write('\n\n')
        counter += 1