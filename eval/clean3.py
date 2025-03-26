import pandas as pd

# Read the CSV file
df = pd.read_csv('/home/loch/python-scripts/Valid_GitHub_Repo_Names_20.csv')

# Function to process the name
def process_name(name):
    parts = name.split('-', 1)
    if len(parts) == 2:
        first_part, second_part = parts
        if second_part.count('-') > 3:
            second_part = second_part.replace('-', '')
        return f"{first_part}-{second_part}"
    return name

# Apply the function to process each name
df['ProcessedOutput'] = df['Output'].apply(process_name)

# Select only the processed names column
processed_names_df = df[['ProcessedOutput']]

# Write the processed names to a new CSV file
processed_names_df.to_csv('/home/loch/python-scripts/Processed_GitHub_Repo_Names_20.csv', index=False)