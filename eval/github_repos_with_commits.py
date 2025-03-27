from github import Github
import csv
from datetime import datetime
from collections import defaultdict

# Replace with your GitHub personal access token and organization name
GITHUB_TOKEN = "xx"
ORGANIZATION_NAME = "ewfx"

# Initialize GitHub instance
g = Github(GITHUB_TOKEN)

def get_repos_with_multiple_commits(org_name):
    # Get the organization
    try:
        org = g.get_organization(org_name)
    except Exception as e:
        print(f"Error accessing organization {org_name}: {str(e)}")
        return {}
    
    # Dictionary to store repos by prefix
    repos_by_prefix = defaultdict(list)
    
    # Get all repositories for the organization
    repos = org.get_repos()
    
    print(f"Found {repos.totalCount} repositories in {org_name}. Processing...")
    
    # Iterate through each repository
    for repo in repos:

        if repo.name in ['help', '.github', 'hackathon-template']:
            continue

        try:
            # Get the prefix (first 5 characters)
            if len(repo.name) >= 5:
                prefix = repo.name[:5]
            else:
                continue
                
            # Get commit count
            commits = repo.get_commits()
            commit_count = commits.totalCount
            
            # Check if repo has more than 1 commit
            if commit_count > 1:
                repo_info = {
                    'repo_name': repo.name,
                    'commit_count': commit_count,
                    'last_updated': repo.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'url': repo.html_url
                }
                repos_by_prefix[prefix].append(repo_info)
                print(f"Added {repo.name} with {commit_count} commits to {prefix} group")
                
        except Exception as e:
            print(f"Error processing {repo.name}: {str(e)}")
            continue
    
    return repos_by_prefix

def save_to_csv(repos_by_prefix, org_name):
    # Define CSV headers
    fieldnames = ['repo_name', 'commit_count', 'last_updated', 'url']
    
    # Timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Process each prefix group
    for prefix, repo_data in repos_by_prefix.items():
        filename = f'{org_name}_{prefix}_repos_{timestamp}.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write repository data
            for repo in repo_data:
                writer.writerow(repo)
        
        print(f"Saved {len(repo_data)} repositories to {filename}")

def main():
    try:
        # Get repositories with multiple commits from organization
        repos_by_prefix = get_repos_with_multiple_commits(ORGANIZATION_NAME)
        
        if repos_by_prefix:
            # Save to separate CSV files
            save_to_csv(repos_by_prefix, ORGANIZATION_NAME)
            total_repos = sum(len(repos) for repos in repos_by_prefix.values())
            print(f"Found {total_repos} repositories with more than 1 commit across {len(repos_by_prefix)} prefix groups")
        else:
            print(f"No repositories found with more than 1 commit in {ORGANIZATION_NAME}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
