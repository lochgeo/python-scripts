import csv
import re
from github import Github
from github.GithubException import GithubException

# Personal Access Token (with admin:org permissions)
access_token = "your_personal_access_token"
# Organization name
org_name = "your_organization_name"
# Path to the CSV file containing the team names
csv_file_path = "teams.csv"
# Template repository name
template_repo_name = "hackathon-template"

# Initialize Github object
g = Github(access_token)

# Function to read team names from CSV file
def read_teams_from_csv(file_path):
    teams = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            teams.append(row['team'])
    return teams

# Function to sanitize team name to kebab case
def sanitize_team_name(team_name):
    return re.sub(r'[^a-zA-Z0-9]+', '-', team_name).lower().strip('-')

try:
    # Get the organization object
    org = g.get_organization(org_name)

    # Read team names from the CSV file
    teams = read_teams_from_csv(csv_file_path)
    
    # Create repositories for each team
    for team in teams:
        repo_name = sanitize_team_name(team)
        try:
            org.create_repo(
                name=repo_name,
                private=False,
                template_repo=org.get_repo(template_repo_name)
            )
            print(f"Repository '{repo_name}' created for team '{team}'")
        except GithubException as e:
            print(f"Failed to create repository for team '{team}': {e.data['message']}")

except GithubException as e:
    print(f"Error accessing organization: {e.data['message']}")