import csv
import logging
import os
import sys
from github import Github, Organization
from github.GithubException import GithubException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("github_team_creation.log"),  # Log to a file
        logging.StreamHandler(sys.stdout),  # Log to console
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables for sensitive data
GITHUB_TOKEN = "xx"
ORG_NAME = "ewfx"

if not GITHUB_TOKEN or not ORG_NAME:
    logger.error("Environment variables GITHUB_TOKEN and ORG_NAME must be set.")
    sys.exit(1)

# Initialize GitHub instance
try:
    g = Github(GITHUB_TOKEN)
    logger.info("GitHub instance initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize GitHub instance: {e}")
    sys.exit(1)


def fetch_all_repos(org: Organization) -> dict:
    """
    Fetch all repositories in the organization using pagination and cache them in a dictionary.

    Args:
        org (Organization): GitHub organization object.

    Returns:
        dict: A dictionary mapping repository names to repository objects.
    """
    repos = {}
    try:
        # Use pagination to fetch all repositories
        for repo in org.get_repos(type="all"):
            repos[repo.name] = repo
        logger.info(f"Fetched {len(repos)} repositories.")
    except GithubException as e:
        logger.error(f"Error fetching repositories: {e}")
    return repos


def fetch_all_teams(org: Organization) -> dict:
    """
    Fetch all teams in the organization and cache them in a dictionary.

    Args:
        org (Organization): GitHub organization object.

    Returns:
        dict: A dictionary mapping team slugs to team objects.
    """
    teams = {}
    try:
        for team in org.get_teams():
            teams[team.slug] = team
        logger.info(f"Fetched {len(teams)} teams.")
    except GithubException as e:
        logger.error(f"Error fetching teams: {e}")
    return teams


def create_team_and_add_repo(org: Organization, team_name: str, repos: dict, teams: dict) -> bool:
    """
    Creates a GitHub team and grants it admin access to a repository with the same name.

    Args:
        org (Organization): GitHub organization object.
        team_name (str): Name of the team and repository.
        repos (dict): Dictionary of cached repositories.
        teams (dict): Dictionary of cached teams.

    Returns:
        bool: True if successful, False otherwise.
    """
    # Check if the repository exists
    if team_name not in repos:
        logger.error(f"Repository {team_name} does not exist.")
        return False

    repo = repos[team_name]
    logger.info(f"Repository found: {team_name}")

    # Check if the team exists
    if team_name in teams:
        logger.warning(f"Team {team_name} already exists.")
        return False

    try:
        # Create a new team
        team = org.create_team(name=team_name)
        logger.info(f"Team created: {team_name}")
    except GithubException as e:
        logger.error(f"Error creating team {team_name}: {e}")
        return False

    try:
        # Add the team to the repository with admin permissions
        team.add_to_repos(repo)
        team.set_repo_permission(repo, "admin")
        logger.info(f"Granted admin access to repository {team_name} for team {team_name}.")
        return True
    except GithubException as e:
        logger.error(f"Error adding team {team_name} to repository {team_name}: {e}")
        return False


def main():
    """Main function to read team names from a CSV file and create teams/repositories."""
    csv_file_path = "/home/loch/python-scripts/Processed_GitHub_Repo_Names_Final_Set.csv"

    try:
        # Read the CSV file
        with open(csv_file_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            team_names = [row[0] for row in reader]
        logger.info(f"Successfully read {len(team_names)} team names from CSV file.")
    except FileNotFoundError:
        logger.error(f"CSV file not found at path: {csv_file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        sys.exit(1)

    try:
        # Get the organization
        org = g.get_organization(ORG_NAME)
        logger.info(f"Successfully retrieved organization: {ORG_NAME}")
    except GithubException as e:
        logger.error(f"Error retrieving organization {ORG_NAME}: {e}")
        sys.exit(1)

    # Fetch all repositories and teams in the organization
    repos = fetch_all_repos(org)
    teams = fetch_all_teams(org)

    # Create teams and add repos
    success_count = 0
    failure_count = 0
    for team_name in team_names:
        logger.info(f"Processing team: {team_name}")
        if create_team_and_add_repo(org, team_name, repos, teams):
            success_count += 1
        else:
            failure_count += 1

    logger.info(f"Process completed. Success: {success_count}, Failures: {failure_count}")


if __name__ == "__main__":
    main()