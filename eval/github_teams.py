import csv
import re
from github import Github
from github.GithubException import GithubException

# Personal Access Token (with admin:org permissions)
access_token = "your_personal_access_token"
# Organization name
org_name = "your_organization_name"
# Path to the CSV file containing the team names and email IDs
csv_file_path = "teams_and_members.csv"

# Initialize Github object
g = Github(access_token)

# Function to read teams and members from CSV file
def read_teams_and_members_from_csv(file_path):
    teams = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            team_name = row['team']
            email = row['email']
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(email)
    return teams

# Function to sanitize team name to kebab case
def sanitize_team_name(team_name):
    return re.sub(r'[^a-zA-Z0-9]+', '-', team_name).lower().strip('-')

try:
    # Get the organization object
    org = g.get_organization(org_name)

    # Read teams and members from the CSV file
    teams = read_teams_and_members_from_csv(csv_file_path)
    
    # Create teams and add members
    for team, members in teams.items():
        team_name = sanitize_team_name(team)
        try:
            # Create the team
            created_team = org.create_team(name=team_name, privacy='closed')
            print(f"Team '{team_name}' created for team '{team}'")
            
            # Add members to the team
            for email in members:
                try:
                    user = g.search_users(email)[0]
                    created_team.add_membership(user)
                    print(f"Added {email} to team '{team_name}'")
                except GithubException as e:
                    print(f"Failed to add {email} to team '{team_name}': {e.data['message']}")
        except GithubException as e:
            print(f"Failed to create team '{team}': {e.data['message']}")

except GithubException as e:
    print(f"Error accessing organization: {e.data['message']}")