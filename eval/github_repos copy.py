import csv
import re
import requests
from github import Github
from github.GithubException import GithubException

# Personal Access Token (with admin:org permissions)
access_token = "xx"
# Organization name
org_name = "ewfx"
# Path to the CSV file containing the team names
csv_file_path = "Processed_GitHub_Repo_Names_Final_Set.csv"
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

    # Verify template repository exists
    template_repo = g.get_repo(f"{org_name}/{template_repo_name}")
    print(f"Successfully found template repository: {template_repo.full_name}")
    
    # Create repositories for each team
    for team in teams[1000:]:
        repo_name = sanitize_team_name(team)
        try:
            # Check if the repository already exists
            org.get_repo(repo_name)
            print(f"Repository '{repo_name}' already exists for team '{team}'")
        except GithubException as e:
            if e.status == 404:
                # Repository does not exist, create it using direct API call
                try:
                    # GitHub API endpoint for creating a repository from a template
                    url = f"https://api.github.com/repos/{org_name}/{template_repo_name}/generate"
                    
                    # Request headers
                    headers = {
                        "Authorization": f"token {access_token}",
                        "Accept": "application/vnd.github.baptiste-preview+json"  # Required for template repositories
                    }
                    
                    # Request body
                    data = {
                        "owner": org_name,
                        "name": repo_name,
                        "description": f"Repository for team: {team}",
                        "private": False
                    }
                    
                    # Make the API request
                    response = requests.post(url, headers=headers, json=data)
                    
                    # Check if the request was successful
                    if response.status_code == 201:
                        print(f"Repository '{repo_name}' created for team '{team}'")
                    else:
                        print(f"Failed to create repository for team '{team}': {response.json()}")
                        print(f"Status code: {response.status_code}")
                except Exception as e:
                    print(f"Error creating repository for team '{team}': {str(e)}")
            else:
                print(f"Error checking repository for team '{team}': {e.data['message']}")

except GithubException as e:
    print(f"Error accessing organization or template repository: {e.data['message']}")
    print(f"Status: {e.status}")