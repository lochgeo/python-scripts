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
    return team_name

# Apply the function to the TeamName column
df['TeamName'] = df['TeamName'].apply(sanitize_team_name)

# Create the new column by joining ChallengeName and sanitized TeamName with a hyphen
df['Output'] = df['ChallengeName'] + '-' + df['TeamName']

# Select only the new column and remove duplicates
output_df = df[['Output']].drop_duplicates()

# Write the output to a new CSV file
output_df.to_csv('/home/loch/python-scripts/Output_Registration_Details_20.csv', index=False)