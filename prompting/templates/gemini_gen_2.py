import google.generativeai as genai
from dotenv import load_dotenv
import os
import pandas as pd
import time

load_dotenv()

df = pd.read_excel('240902_Sample risk data SMU.xlsx')
des = df['Description']

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
counter = 1

# Risk Identification given 3 choices, last choice as Port Disruption.
for i in des:
   response = model.generate_content(f"""Given the following text: 

    {i}

    ## Your Role
    You are a consultant specialized in maritime and international trading. You must accurately classify the type of port risk based on collected newspaper articles.
    This is extremely important as any inaccurate classification can lead to a loss of over a million dollars due to suboptimal route planning. 

    ## Your Task
    - There are 4 main risks: Port Strike, Port Disruption, Port Closure, and Port Congestion. Print what you know about the difference between the different risks.
    - Based on the articles given, think step by step and provide the final risk classification.
    - You must give a risk classification.
    - After giving your final answer, think: are you sure of it? Reflect on it and provide a new answer if you are unsure.
    """)
   with open('..\\output\\gemini_risk_identification_2.txt', 'a') as f:
      f.write(str(counter) + '. ')
      f.write(response.text)
      f.write('\n\n')
      counter += 1
   time.sleep(5)