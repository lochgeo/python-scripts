import csv
from github import Github
from github.GithubException import GithubException

# Personal Access Token (with admin:org permissions)
access_token = "xx"
# Organization name
org_name = "ewfx"
# Path to the CSV file containing the emails
csv_file_path = "Processed_GitHub_Repo_Names_Final_Set.csv"

# Initialize Github object
g = Github(access_token)

# Function to read emails from CSV file
def read_emails_from_csv(file_path):
    emails = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            emails.append(row['email'])
    return emails

try:
    # Get the organization object
    org = g.get_organization(org_name)

    # Read emails from the CSV file
    emails = read_emails_from_csv(csv_file_path)
    
    # Invite users via email
    for email in emails:
        try:
            org.invite_user(email=email)
            print(f"Invitation sent to {email}")
        except GithubException as e:
            print(f"Failed to invite {email}: {e.data['message']}")

except GithubException as e:
    print(f"Error accessing organization: {e.data['message']}")
