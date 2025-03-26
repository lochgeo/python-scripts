import csv
from github import Github
from github.GithubException import GithubException, RateLimitExceededException, UnknownObjectException
import time
import ast
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("github_collaborators.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Personal Access Token (with repo and admin:org permissions)
access_token = "xx"
# Organization name
org_name = "ewfx"
# Path to the CSV file containing the repo names and emails
csv_file_path = "/home/loch/python-scripts/Processed_GitHub_Repo_Names_With_Emails_20_2_output.csv"
# Rate limit protection - pause seconds
RATE_LIMIT_PAUSE = 1
# Batch size for processing repositories
BATCH_SIZE = 10

# Initialize Github object with increased page size
g = Github(access_token, per_page=100)

# Function to read repo names and emails from CSV file - optimized
def read_repos_and_emails_from_csv(file_path):
    repos_and_emails = {}
    with open(file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            repo_name = row["ProcessedOutput"]
            # Safer eval using literal_eval
            try:
                emails = ast.literal_eval(row["PersonalEmail"])
            except (ValueError, SyntaxError):
                logger.warning(f"Could not parse emails for {repo_name}, skipping")
                continue
            repos_and_emails[repo_name] = emails
    return repos_and_emails

# Cache for user lookups to avoid repetitive API calls
user_cache = {}

# Retry decorator for GitHub API calls
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitExceededException, GithubException)),
)
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
        logger.error(f"Failed to lookup user by email {email}: {e}")
        user_cache[email] = None
        return None

def process_repository(repo_name, emails, org):
    """Process a single repository and add collaborators"""
    try:
        repo = org.get_repo(repo_name)
        logger.info(f"Processing repository: {repo_name}")

        # Get existing collaborators to avoid redundant additions
        existing_collaborators = set(collab.login for collab in repo.get_collaborators())

        # Get teams that have access to the repository
        repo_teams = repo.get_teams()
        team_members = set()

        # Get all team members for each team that has access to the repo
        for team in repo_teams:
            for member in team.get_members():
                team_members.add(member.login)

        logger.info(f"Found {len(team_members)} team members with access to {repo_name}")

        for email in emails:
            try:
                # Try to get user by email (with caching)
                user = get_user_by_email(email)

                if user:
                    # Check if user is already a collaborator or part of a team with access
                    if user.login in existing_collaborators:
                        logger.info(f"User {email} is already a direct collaborator on {repo_name}")
                    elif user.login in team_members:
                        logger.info(f"User {email} already has access to {repo_name} via team membership")
                    else:
                        repo.add_to_collaborators(user.login, permission="pull")
                        logger.info(f"Added {email} as a collaborator to {repo_name}")
                        time.sleep(RATE_LIMIT_PAUSE)  # Pause to avoid rate limits
                else:
                    # If the user is not found, invite them by email
                    repo.add_to_collaborators(email, permission="pull")
                    logger.info(f"Invitation sent to {email} to collaborate on {repo_name}")
                    time.sleep(RATE_LIMIT_PAUSE)  # Pause to avoid rate limits

            except UnknownObjectException as e:
                logger.error(f"User or repository not found for {email} in {repo_name}: {e}")
            except GithubException as e:
                logger.error(f"Failed to add {email} to {repo_name}: {e}")

    except UnknownObjectException as e:
        logger.error(f"Repository {repo_name} not found in organization {org_name}: {e}")
    except GithubException as e:
        logger.error(f"Failed to access repository {repo_name}: {e}")

def main():
    try:
        # Verify organization access before processing
        org = g.get_organization(org_name)
        logger.info(f"Successfully connected to organization: {org_name}")

        # Read repo names and emails from the CSV file
        repos_and_emails = read_repos_and_emails_from_csv(csv_file_path)
        logger.info(f"Found {len(repos_and_emails)} repositories to process")

        # Process repositories in batches
        repo_items = list(repos_and_emails.items())
        for i in range(0, len(repo_items), BATCH_SIZE):
            batch = repo_items[i : i + BATCH_SIZE]
            for repo_name, emails in batch:
                process_repository(repo_name, emails, org)
            logger.info(f"Processed batch {i // BATCH_SIZE + 1}")

    except GithubException as e:
        logger.error(f"Error accessing organization: {e.data['message']}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()