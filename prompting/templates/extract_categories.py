import re
import pandas as pd

def extract_risk_info(file_path, df):
    # Pattern to match {number}. followed by any string
    pattern = r"^(\d+)\.\s*(.*)"

    df["Risk Type"] = ""

    # Open the file and read lines
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                number = int(match.group(1))
                risk = ""
                if "Port Acquisition" in line:
                    risk = "Port Acquisition"
                elif "Port Attack" in line:
                    risk = "Port Attack"
                elif "Port Closure" in line:
                    risk = "Port Closure"
                elif "Port Collision" in line:
                    risk = "Port Collision"
                elif "Port Congestion" in line:
                    risk = "Port Congestion"
                elif "Port Contamination" in line:
                    risk = "Port Contamination"
                elif "Port Corruption" in line:
                    risk = "Port Corruption"
                elif "Port Delay" in line:
                    risk = "Port Delay"
                elif "Port Detention" in line:
                    risk = "Port Detention"
                elif "Port Disruption" in line:
                    risk = "Port Disruption"
                elif "Port Hijacking" in line:
                    risk = "Port Hijacking"
                elif "Port Infiltration" in line:
                    risk = "Port Infiltration"
                elif "Port Piracy" in line:
                    risk = "Port Piracy"
                elif "Port Seizure" in line:
                    risk = "Port Seizure"
                elif "Port Strike" in line:
                    risk = "Port Strike"
                elif "None" in line:
                    risk = "None"
    
                df.iloc[number - 1, df.columns.get_loc("Risk Type")] = risk 

    return df

text_file_path = '../output/overall/prompt_and_cleaned/risk_identification.txt'
excel_file_path = 'EDA_output5.xlsx'

df = pd.read_excel(excel_file_path, index_col=0)

updated_df = extract_risk_info(text_file_path, df)

output_excel_path = 'Extract_Categories_output5.xlsx'
updated_df.to_excel(output_excel_path)

print("Risk information has been mapped and saved to", output_excel_path)
