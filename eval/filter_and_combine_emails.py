import csv
from collections import defaultdict

# Define the input and output file paths
input_file = '/home/loch/python-scripts/Processed_GitHub_Repo_Names_With_Emails_Final_Set.csv'
output_file = '/home/loch/python-scripts/Processed_GitHub_Repo_Names_With_Emails_Final_Set_output.csv'

# Initialize a dictionary to store the emails associated with each team name
team_emails = defaultdict(list)

# Read the input CSV file
with open(input_file, mode='r') as infile:
    reader = csv.reader(infile)
    header = next(reader)  # Skip the header row
    for row in reader:
        team_name = row[0]
        emails = row[1].split(',') if row[1] else []
        # Filter out emails with wellsfargo.com domain
        filtered_emails = [email for email in emails if 'wellsfargo' not in email]
        team_emails[team_name].extend(filtered_emails)

# Write the output CSV file
with open(output_file, mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['ProcessedOutput', 'PersonalEmail'])  # Write the header row
    for team_name, emails in team_emails.items():
        writer.writerow([team_name, emails])