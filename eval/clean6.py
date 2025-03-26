import csv
from github import Github, Organization
from github.GithubException import GithubException

# Replace with your GitHub token
GITHUB_TOKEN = 'xx'

# Initialize GitHub instance
g = Github(GITHUB_TOKEN)

# Replace with your organization name
ORG_NAME = 'ewfx'

def create_team_and_add_repo(org: Organization, team_name):
    try:
        # Check if the repository exists
        repo = org.get_repo(team_name)
        print(f'Repository found: {team_name}')
    except GithubException as e:
        print(f'Repository {team_name} does not exist: {e}')
        return

    try:
        # Check if the team exists
        team = org.get_team_by_slug(team_name)
        print(f'Team {team_name} already exists')
        return
    except GithubException:
        # Team does not exist, proceed to create it
        pass

    try:
        # Create a new team
        team = org.create_team(name=team_name)
        print(f'Team created: {team_name}')
    except GithubException as e:
        print(f'Error creating team {team_name}: {e}')
        return

    try:
        # Add the team to the repository with admin permissions
        team.add_to_repos(repo)
        team.set_repo_permission(repo, 'admin')
        print(f'Granted admin access to {team_name} for team {team_name}')
    except GithubException as e:
        print(f'Error adding team {team_name} to repo {team_name}: {e}')

def main():
    # Read the CSV file
    with open('/home/loch/python-scripts/Processed_GitHub_Repo_Names_Final_Set.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        team_names = [row[0] for row in reader]

    # Get the organization
    org = g.get_organization(ORG_NAME)

    # Create teams and add repos
    for team_name in team_names:
        create_team_and_add_repo(org, team_name)

if __name__ == '__main__':
    main()