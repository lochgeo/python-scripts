import pandas as pd
import re

# Read CSV
df = pd.read_csv('/home/loch/python-scripts/Registration_Details_Final_Set.csv')

# Vectorized Sanitization for Team Names
def sanitize_team_names(series):
    replacements = {
        '_': '-', ' ': '-', '.': '-', '#': 'hash-', '$': 's', '*': '', 
        '+': '-', '&': '-', "'": '-', ':': '-', '/': '-', '\\': '-', 
        '<': '-', '>': '-', '@': 'a'
    }
    
    special_replacements = {
        'a-i': 'ai', 'l-l-m': 'llm', 'g-p-t': 'gpt'
    }
    
    # Insert hyphen before capital letters (CamelCase handling)
    series = series.str.replace(r'(?<!^)(?=[A-Z])', '-', regex=True)
    
    series = series.fillna('').str.lower()
    
    # Apply character replacements
    for old, new in replacements.items():
        series = series.str.replace(old, new, regex=False)


    # Apply word replacements
    for old, new in special_replacements.items():
        series = series.str.replace(old, new, regex=False)

    # Replace multiple hyphens with a single hyphen
    return series.str.replace(r'-+', '-', regex=True)


df['TeamName'] = sanitize_team_names(df['TeamName'])

# Create GitHub Repo Names
df['Output'] = df['ChallengeName'] + '-' + df['TeamName']

# Vectorized GitHub Name Validation
def is_valid_github_repo_name(series):
    valid_length = series.str.len().between(1, 100)
    valid_chars = series.str.match(r'^[a-zA-Z0-9]+([a-zA-Z0-9-]*[a-zA-Z0-9])?$')
    no_double_hyphens = ~series.str.contains('--', regex=False)
    return valid_length & valid_chars & no_double_hyphens

df['IsValid'] = is_valid_github_repo_name(df['Output'])

# Identify Invalid Names
invalid_mask = ~df['IsValid']
if invalid_mask.any():
    print("Invalid Team Names:", df.loc[invalid_mask, 'TeamName'].unique())

# Fix Invalid Names
def fix_invalid_names(series):
    return (
        series.str.replace(r'[/.\'()&]', '', regex=True)  # Remove special characters except numbers
        .str.replace(r'(?<=\D)(\d)', r'-\1', regex=True)  # Insert hyphen before first number if preceded by a letter
        .str.replace('-+', '-', regex=True)  # Replace multiple hyphens
        .str.strip('-')  # Remove leading/trailing hyphens
    )

df.loc[invalid_mask, 'Output'] = fix_invalid_names(df.loc[invalid_mask, 'Output'])

# Re-check validity after fixing
df['IsValid'] = is_valid_github_repo_name(df['Output'])

# Filter Valid Names
valid_names_df = df[df['IsValid']].copy()

# Vectorized Processing of Repo Names
def process_names(series):
    parts = series.str.split('-', n=1, expand=True)
    has_extra_hyphens = parts[1].str.count('-') > 3
    parts.loc[has_extra_hyphens, 1] = parts.loc[has_extra_hyphens, 1].str.replace('-', '', regex=False)
    return parts[0] + '-' + parts[1]

valid_names_df['ProcessedOutput'] = process_names(valid_names_df['Output'])

# Select Final Data
final_df = valid_names_df[['ProcessedOutput', 'PersonalEmail']]

# Save to CSV
final_df.to_csv('/home/loch/python-scripts/Processed_GitHub_Repo_Names_With_Emails_Final_Set.csv', index=False)
