import csv
from github import Github
from github.GithubException import GithubException

# Personal Access Token (with admin:org permissions)
access_token = "xx"
# Organization name
org_name = "ewfx"
# Path to the input CSV file containing the repository names
input_csv_file_path = "/home/loch/python-scripts/Processed_GitHub_Repo_Names_20.csv"
# Path to the output CSV file for non-existent repositories
output_csv_file_path = "/home/loch/python-scripts/NonExistentRepos.csv"

# Initialize Github object
g = Github(access_token)

# Function to read repository names from CSV file
def read_repo_names_from_csv(file_path):
    repo_names = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            repo_names.append(row['ProcessedOutput'])
    return repo_names

# Function to write non-existent repository names to CSV file
def write_non_existent_repos_to_csv(file_path, non_existent_repos):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['NonExistentRepos'])
        for repo in non_existent_repos:
            writer.writerow([repo])

try:
    # Get the organization object
    org = g.get_organization(org_name)

    # Read repository names from the CSV file
    repo_names = read_repo_names_from_csv(input_csv_file_path)
    
    # List to store non-existent repositories
    non_existent_repos = []

    # Check if repositories exist in the organization
    for repo_name in repo_names:
        try:
            org.get_repo(repo_name)
            print(f'Repository exists: {repo_name}')
        except GithubException:
            print(f'Repository does not exist: {repo_name}')
            non_existent_repos.append(repo_name)

    # Write non-existent repositories to the output CSV file
    write_non_existent_repos_to_csv(output_csv_file_path, non_existent_repos)

except GithubException as e:
    print(f"Error accessing organization: {e.data['message']}")