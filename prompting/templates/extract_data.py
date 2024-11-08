import re
import pandas as pd

def extract_risk_info(file_path):
    # Define a list to store event data
    data = []
    # Open and read the file
    with open(file_path, 'r') as file:
        content = file.read()
        events = re.split(r'\n\d+\.\s+', content)

        for event in events[1:]:  # Skip the first item since it's empty
            # Extract key information using regex
            disruption_event = re.search(r"Disruption event:\s*(.*)\n", event)
            port_affected = re.search(r"Port Affected:\s*(.*)", event)
            date = re.search(r"Date:\s*(.*)", event)
            final_classification = re.search(r"Final Classification:\s*\*\*(.*)\*\*", event)
            
            # Append extracted data as a dictionary
            data.append({
                "Disruption Event": disruption_event.group(1).strip() if disruption_event else None,
                "Port Affected": port_affected.group(1).strip() if port_affected else None,
                "Date": date.group(1).strip() if date else None,
                "Final Classification": final_classification.group(1).strip() if final_classification else None
            })
        return data

text_file_path = '../output/filtered_overall/prompt_and_cleaned/risk_identification5.txt'
excel_file_path = 'input.xlsx'

df = pd.read_excel(excel_file_path, index_col=0)
df['Final Classification'] = ""
df['Disruption Event'] = ""
df['Date Item'] = ""
df['Affected Port'] = ""
sections = extract_risk_info(text_file_path)
# print(sections[13])
for i in range(3751, len(sections) + 3751):
    row = sections[i - 3751]
    df.iloc[i + 1, df.columns.get_loc("Disruption Event")] = re.sub(r"[#*]+", "", row['Disruption Event'] or "").strip()
    df.iloc[i + 1, df.columns.get_loc("Affected Port")] = re.sub(r"[#*]+", "", row['Port Affected'] or "").strip()
    df.iloc[i + 1, df.columns.get_loc("Date Item")] = re.sub(r"[#*]+", "", row['Date'] or "").strip()
    df.iloc[i + 1, df.columns.get_loc("Final Classification")] = re.sub(r"[#*]+", "", row['Final Classification'] or "").strip()

output_excel_path = 'output_excel.xlsx'
df.to_excel(output_excel_path)

print("Risk information has been mapped and saved to", output_excel_path)
