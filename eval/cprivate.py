from github import Github
from github.Repository import Repository
from github.GithubException import GithubException
import logging

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("github_repos_private.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# GitHub Personal Access Token (with repo and admin:org permissions)
access_token = "xx"
# Organization name
org_name = "ewfx"
# Username to exclude (lochgeo)
EXCLUDED_USER = ["lochgeo", "venkatukl", "ashishajr", "ganeshgowtham", "tech2avinash", "anugjoseph", "ezhilanradha", "sumanthkumar"]

# Initialize GitHub object
g = Github(access_token)

def get_private_repos(org_name: str, token: str):
    """
    Fetch all private repositories from a given GitHub organization.

    :param org_name: The name of the GitHub organization.
    :param token: A GitHub personal access token with necessary permissions.
    :return: A list of private repository names.
    """
    try:
        g = Github(token)
        org = g.get_organization(org_name)
        private_repos = [repo for repo in org.get_repos(type='private')]
        return private_repos
    except Exception as e:
        print(f"Error fetching repositories: {e}")
        return []

def has_other_collaborators(repo: Repository, excluded_users):
    """Check if the repository has collaborators other than the excluded user."""
    collaborators = repo.get_collaborators(permission="admin")
    for collaborator in collaborators:
        if collaborator.login not in excluded_users:
            return True
    return False

def has_other_team_members_with_push(repo, excluded_users):
    """Check if the repository has team members with push rights other than the excluded users."""
    teams = repo.get_teams()
    for team in teams:
        # Check the team's permission level for the repository
        team_permission = team.get_repo_permission(repo)
        if team_permission.admin == True:  # 'write' means push access
            members = team.get_members()
            for member in members:
                if member.login not in excluded_users:
                    return True
    return False

def mark_repositories_private(org_name, excluded_user):
    """Mark repositories as private if they have collaborators or team members other than the excluded user."""
    try:
        # Get the organization
        org = g.get_organization(org_name)
        logger.info(f"Successfully connected to organization: {org_name}")

        # Get all repositories in the organization
        repos = get_private_repos(org_name, access_token)
        logger.info(f"Found {len(repos)} repositories in the organization")

        # Process each repository
        for repo in repos:
            
            if repo.name in [ "help", "hackathon-template"]:
                continue

            try:
                logger.info(f"Processing repository: {repo.name}")

                if repo.private:
                    repo.edit(private=False)

            except GithubException as e:
                logger.error(f"Failed to process repository {repo.name}: {e}")

    except GithubException as e:
        logger.error(f"Error accessing organization: {e.data['message']}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def mark_repositories_private_2(org_name, excluded_user):
    """Mark repositories as private if they have collaborators or team members other than the excluded user."""
    try:
        # Get the organization
        org = g.get_organization(org_name)
        logger.info(f"Successfully connected to organization: {org_name}")

        # Get all repositories in the organization
        repos = get_private_repos(org_name, access_token)
        logger.info(f"Found {len(repos)} repositories in the organization")

        # Process each repository
        for repo in repos:
            
            if repo.name in [ "help", "hackathon-template"]:
                continue

            try:
                logger.info(f"Processing repository: {repo.name}")


                if repo.private:
                    repo.edit(private=False)

            except GithubException as e:
                logger.error(f"Failed to process repository {repo.name}: {e}")

    except GithubException as e:
        logger.error(f"Error accessing organization: {e.data['message']}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    mark_repositories_private(org_name, EXCLUDED_USER)
    #count_repositories_eligible_for_private(org_name, EXCLUDED_USER)