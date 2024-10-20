import os
from dotenv import load_dotenv
from github import Github

def archive_org_repos(g, organization_name):
    
    #dont archive the template
    exclude_list = ["nitkhackathon2024/nitk-hackathon-template"]

    try:
        # Get the organization
        org = g.get_organization(organization_name)

        # Iterate through all repositories in the organization
        for repo in org.get_repos():

            if repo.full_name in exclude_list:
                print(f"Skipping repository: {repo.name} as it is in the exclude list")
                continue
                      
            if not repo.archived:
                print(f"Archiving repository: {repo.name}")
                try:
                    repo.edit(archived=True)
                except Exception as e:
                    print(f"Failed to archive repository {repo.name}: {str(e)}")
                    continue
                print(f"Successfully archived: {repo.name}")
            else:
                print(f"Repository already archived: {repo.name}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Usage example
if __name__ == "__main__":
    orgs = ["nitkhackathon2024"]
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    g = Github(github_token)

    for org_name in orgs:
        print("processing", org_name)
        archive_org_repos(g, org_name)

    g.close()