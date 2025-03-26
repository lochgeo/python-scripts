import pandas as pd
import re

# Read the CSV file
df = pd.read_csv('/home/loch/python-scripts/Output_Registration_Details_20.csv')

# Function to check if a name is a valid GitHub repository name
def is_valid_github_repo_name(name):
    if not (1 <= len(name) <= 100):
        return False
    if not re.match(r'^[a-zA-Z0-9]+([a-zA-Z0-9-]*[a-zA-Z0-9])?$', name):
        return False
    if '--' in name:
        return False
    return True

# Apply the function to check each name
df['IsValid'] = df['Output'].apply(is_valid_github_repo_name)

# Filter the valid names
valid_names_df = df[df['IsValid']]

# Select only the valid names column
valid_names_df = valid_names_df[['Output']]

# Write the valid names to a new CSV file
valid_names_df.to_csv('/home/loch/python-scripts/Valid_GitHub_Repo_Names_20.csv', index=False)