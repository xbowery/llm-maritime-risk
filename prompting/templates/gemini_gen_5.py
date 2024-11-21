import google.generativeai as genai
from dotenv import load_dotenv
import os
import pandas as pd
import time
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()
os.makedirs('../output/filtered_overall/prompt_and_cleaned', exist_ok=True)

df = pd.read_excel('EDA_Filtered_output5.xlsx')

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
counter = 1

for index, row in df.iterrows():
   response = model.generate_content(f"""Given the following text:

    Headline: '{row["Cleaned_Headline"]}'
    Content: '{row["Cleaned_Description"]}'

    ## Your Role
    You are a consultant specialized in maritime and international trading. 
    This is extremely important because any inaccurate classification or lack of details can lead to a loss of over a million dollars due to suboptimal route planning.

    ## Your Task
    - Provide the final risk classification based on the article given. If unsure, reflect and revise if necessary. The categories you can include are:
        - Vessel Delay: Delays in vessel schedules affecting port operations and shipping timelines.
        - Vessel Accidents: Accidents involving vessels, impacting safety, cargo, and port operations.
        - Maritime Piracy/Terrorism Risk: Risks from piracy or terrorism targeting vessels, cargo, or routes.
        - Port or Important Route Congestion: Congestion at ports or critical routes, delaying vessel movement.
        - Port Criminal Activities: Illegal activities at ports, impacting security and cargo safety.
        - Cargo Damage and Loss: Loss or damage to cargo during transportation or handling processes.
        - Inland Transportation Risks: Risks in land transport affecting cargo or vessel schedules.
        - Environmental Impact and Pollution: Pollution or environmental damage caused by maritime activities or spills.
        - Natural Extreme Events and Extreme Weather: Severe weather or natural events affecting maritime routes or ports.
        - Cargo or Ship Detainment: Cargo or vessels detained due to inspections, regulations, or disputes.
        - Unstable Regulatory and Political Environment: Political instability or regulatory changes affecting maritime operations.
        - Others: Maritime events outside predefined categories requiring separate classification.
        - Not maritime-related: Events unrelated to maritime activities or not impacting the maritime sector.

    ### Format
    Final Classification: <classification>
    """,
  safety_settings={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE
  })
   with open('../output/filtered_overall/prompt_and_cleaned/risk_identification.txt', 'a') as f:
      f.write(str(counter) + '. ')
      f.write(response.text)
      f.write('\n\n')
      counter += 1
   time.sleep(5)
