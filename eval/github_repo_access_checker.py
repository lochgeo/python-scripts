import csv
from github import Github
from github.GithubException import GithubException
import time
import ast
import json

# Personal Access Token (with repo and admin:org permissions)
access_token = "xx"
# Organization name
org_name = "ewfx"
# Path to the CSV file containing the repo names and emails
csv_file_path = "/home/loch/python-scripts/Processed_GitHub_Repo_Names_With_Emails_20_2_output.csv"
# Output file path for users without access
output_file_path = "/home/loch/python-scripts/users_without_access.csv"

# Initialize Github object with increased page size
g = Github(access_token, per_page=100)

# Function to read repo names and emails from CSV file - optimized
def read_repos_and_emails_from_csv(file_path):
    repos_and_emails = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            repo_name = row['ProcessedOutput']
            # Safer eval using literal_eval
            try:
                emails = ast.literal_eval(row['PersonalEmail'])
            except (ValueError, SyntaxError):
                print(f"Warning: Could not parse emails for {repo_name}, skipping")
                continue
            repos_and_emails[repo_name] = emails
    return repos_and_emails

# Cache for user lookups to avoid repetitive API calls
user_cache = {}

def get_user_by_email(email):
    """Get user with caching to reduce API calls"""
    if email in user_cache:
        return user_cache[email]
    
    try:
        # PyGithub doesn't provide a direct method to get user by email
        # We need to search for users instead
        users = g.search_users(f"{email} in:email")
        if users.totalCount > 0:
            user = users[0]
            user_cache[email] = user
            return user
        else:
            user_cache[email] = None
            return None
    except GithubException as e:
        user_cache[email] = None
        return None

def main():
    users_without_access = {}  # Dictionary to store repo names and emails without access
    
    try:
        # Verify organization access before processing
        org = g.get_organization(org_name)
        print(f"Successfully connected to organization: {org_name}")
        
        # Read repo names and emails from the CSV file
        repos_and_emails = read_repos_and_emails_from_csv(csv_file_path)
        print(f"Found {len(repos_and_emails)} repositories to process")
        
        # Process repositories sequentially
        for repo_name, emails in repos_and_emails.items():
            try:
                print(f"Processing repository: {repo_name}")
                repo = org.get_repo(repo_name)
                
                # Get existing collaborators
                print(f"Getting existing collaborators for {repo_name}...")
                existing_collaborators = set(collab.login for collab in repo.get_collaborators())
                
                # Get teams that have access to the repository
                print(f"Getting teams with access to {repo_name}...")
                repo_teams = repo.get_teams()
                team_members = set()
                
                # Get all team members for each team that has access to the repo
                for team in repo_teams:
                    for member in team.get_members():
                        team_members.add(member.login)
                
                print(f"Found {len(team_members)} team members with access to {repo_name}")
                
                # Check each email
                emails_without_access = []
                for email in emails:
                    try:
                        # Try to get user by email
                        user = get_user_by_email(email)
                        
                        if user:
                            # Check if user already has access
                            if user.login in existing_collaborators or user.login in team_members:
                                print(f"User {email} already has access to {repo_name}")
                            else:
                                # User exists but doesn't have access
                                print(f"User {email} does not have access to {repo_name}")
                                emails_without_access.append(email)
                        else:
                            # User not found by email search, assume they don't have access
                            print(f"User with email {email} not found or doesn't have access to {repo_name}")
                            emails_without_access.append(email)
                            
                    except GithubException as e:
                        print(f"Error checking access for {email} on {repo_name}: {e}")
                        emails_without_access.append(email)
                
                # If there are emails without access for this repo, add them to our dictionary
                if emails_without_access:
                    users_without_access[repo_name] = emails_without_access
            
            except GithubException as e:
                print(f"Failed to access repository {repo_name}: {e}")
                # If we can't access the repo, assume all emails need access
                users_without_access[repo_name] = emails
        
        # Write results to CSV file
        print(f"Writing results to {output_file_path}")
        with open(output_file_path, 'w', newline='') as csvfile:
            fieldnames = ['Repository', 'Emails']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for repo_name, emails in users_without_access.items():
                writer.writerow({
                    'Repository': repo_name,
                    'Emails': json.dumps(emails)  # Convert list to JSON string
                })
        
        print(f"Successfully wrote output to {output_file_path}")
        print(f"Found {len(users_without_access)} repositories with users needing access")
                
    except GithubException as e:
        print(f"Error accessing organization: {e.data['message']}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()