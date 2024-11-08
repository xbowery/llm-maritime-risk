import pandas as pd

excel_file_path = "../prompting/templates/EDA_output5.xlsx"
df = pd.read_excel(excel_file_path, index_col=0)

# Function to filter descriptions based on link content
def filter_description(row):
    description = row['description']
    
    if 'gcaptain' in row['link']:
        # Remove everything after 'Join gCaptain'
        filtered = description.split('(Reporting', 1)[0].strip()
        filtered = filtered.split('(Editing', 1)[0].strip()
        filtered = filtered.split('Join the members that receive our newsletter', 1)[0].strip()
    
    elif 'loadstar' in row['link']:
        # Split on '...' and only keep the 0th index
        filtered = description.split('...', 1)[0]
        # On the 0th index, split on '.' and remove the last element
        parts = filtered.split('.')
        if len(parts) > 1:
            filtered = '.'.join(parts[:-1]).strip()
    
    else:
        # If neither 'gcaptain' nor 'loadstar' in link, keep the original description
        filtered = description
    
    return filtered

# Apply the function to the DataFrame and store in a new column 'filtered_description'
df['filtered_description'] = df.apply(filter_description, axis=1)

output_excel_path = 'Filtered_output5.xlsx'
df.to_excel(output_excel_path)
