import google.generativeai as genai
import os
import pandas as pd
import time

df = pd.read_excel('240902_Sample risk data SMU.xlsx')
des = df['Description']

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
counter = 1

# Risk Identification given 3 choices, last choice as Port Disruption.
for i in des:
   response = model.generate_content(f"Given the following text: \n\n\n\
      {i}\n\n\n\
      Categorize the main risk that is affecting the port activities out of the following: Port Strike, Port Congestion, Port Closure.\n\
      If the text does not fit into any of the above, classify it as Port Disruption.")
   with open('gemini_risk_identification.txt', 'a') as f:
      f.write(str(counter) + '. ')
      f.write(response.text)
      f.write('\n\n')
      counter += 1
   time.sleep(5)