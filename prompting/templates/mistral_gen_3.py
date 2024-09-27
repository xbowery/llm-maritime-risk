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
    prompt = f"""Given the following text: \n\n\n\
      {description}\n\n\n\
      Categorize the main risk that is affecting the port activities out of the following: Port Strike, Port Congestion, Port Closure.\n\
      If the text does not fit into any of the above, classify it as Port Disruption.\n\n\
      Output only the final classification and nothing else."""
    
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
        
        with open('..\\output\\mistral\\cleaned\\risk_identification.txt', 'a') as f:
            f.write(str(counter) + '. ')
            f.write(result)
            f.write('\n\n')
        
        counter += 1
        
        time.sleep(5)
        
    except Exception as e:
        print(f"Error on description {counter}: {e}")
        with open('..\\output\\mistral\\cleaned\\risk_identification.txt', 'a') as f:
            f.write(str(counter) + '. ')
            f.write("Error occurred")
            f.write('\n\n')
        counter += 1