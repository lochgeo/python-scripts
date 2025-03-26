import pandas as pd
import re

# Read the CSV file
df = pd.read_csv('/home/loch/python-scripts/Registration_Details_20.csv')

# Function to sanitize and format the TeamName
def sanitize_team_name(team_name):
    if pd.isna(team_name):
        return ''
    # Replace underscores and spaces with hyphens
    team_name = team_name.replace('_', '-').replace(' ', '-')
    # Insert hyphens before capital letters (camel case) and after them
    team_name = re.sub(r'(?<!^)(?=[A-Z])', '-', team_name)
    # Convert to lower case
    team_name = team_name.lower()
    # Replace multiple hyphens with a single hyphen
    team_name = re.sub(r'-+', '-', team_name)
    # Replace specific strings
    team_name = team_name.replace('a-i', 'ai').replace('l-l-m', 'llm')
    return team_name

# Apply the function to the TeamName column
df['TeamName'] = df['TeamName'].apply(sanitize_team_name)

# Create the new column by joining ChallengeName and sanitized TeamName with a hyphen
df['Output'] = df['ChallengeName'] + '-' + df['TeamName']

# Function to check if a name is a valid GitHub repository name
def is_valid_github_repo_name(name):
    if not (1 <= len(name) <= 100):
        return False
    if not re.match(r'^[a-zA-Z0-9]+([a-zA-Z0-9-]*[a-zA-Z0-9])?$', name):
        return False
    if '--' in name:
        return False
    return True

# Function to attempt to make invalid names valid
def make_valid_github_repo_name(name):
    # Remove invalid characters
    name = re.sub(r'[/.\'()&]', '', name)
    # Replace multiple hyphens with a single hyphen
    name = re.sub(r'-+', '-', name)
    return name

# Apply the function to check each name
df['IsValid'] = df['Output'].apply(is_valid_github_repo_name)

# Print invalid team names to the console
invalid_names = df[~df['IsValid']]['TeamName'].unique()
print("Invalid Team Names:")
for name in invalid_names:
    print(name)

# Attempt to make invalid names valid
df.loc[~df['IsValid'], 'Output'] = df.loc[~df['IsValid'], 'Output'].apply(make_valid_github_repo_name)

# Re-check validity after attempting to fix names
df['IsValid'] = df['Output'].apply(is_valid_github_repo_name)

# Filter the valid names
valid_names_df = df[df['IsValid']]

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
valid_names_df['ProcessedOutput'] = valid_names_df['Output'].apply(process_name)

# Select the processed names and email columns
final_df = valid_names_df[['ProcessedOutput', 'PersonalEmail']]

# Write the final output to a new CSV file
final_df.to_csv('/home/loch/python-scripts/Processed_GitHub_Repo_Names_With_Emails_20_1.csv', index=False)