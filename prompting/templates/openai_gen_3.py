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
    prompt = f"""Given the following text:\n\n\
    {description}\n\n\
    Categorize the main risk that is affecting the port activities out of the following: Port Strike, Port Congestion, Port Closure.\n\
    If the text does not fit into any of the above, classify it as Port Disruption."""
    
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
        
        with open('..\\output\\openai\\cleaned\\risk_identification.txt', 'a') as f:
            f.write(str(counter) + '. ')
            f.write(result)
            f.write('\n\n')
        
        counter += 1
        
        time.sleep(5)
        
    except Exception as e:
        print(f"Error on description {counter}: {e}")
        with open('..\\output\\openai\\cleaned\\risk_identification.txt', 'a') as f:
            f.write(str(counter) + '. ')
            f.write("Error occurred")
            f.write('\n\n')
        counter += 1