import csv
import logging
import time
import os
import sys
from github import Github
from github.GithubException import GithubException, RateLimitExceededException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("github_invitations.log"),  # Log to a file
        logging.StreamHandler(sys.stdout),  # Log to console
    ],
)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
access_token = "xx"
org_name = "ewfx"
csv_file_path = "Unique_Emails_Final_Set.csv"

if not access_token or not org_name:
    logger.error("Environment variables GITHUB_TOKEN and ORG_NAME must be set.")
    sys.exit(1)

# Initialize Github object
try:
    g = Github(access_token)
    logger.info("GitHub instance initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize GitHub instance: {e}")
    sys.exit(1)


def read_emails_from_csv(file_path):
    """Reads email addresses from a CSV file."""
    emails = []
    try:
        with open(file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if "email" in row:
                    emails.append(row["email"].strip())
        logger.info(f"Successfully read {len(emails)} emails from CSV file.")
    except FileNotFoundError:
        logger.error(f"CSV file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        sys.exit(1)
    return emails


def fetch_all_members(org):
    """Fetches all members of the organization."""
    member_logins = set()
    try:
        for member in org.get_members():
            member_logins.add(member.login)
        logger.info(f"Fetched {len(member_logins)} members.")
    except GithubException as e:
        logger.error(f"Error fetching members: {e}")
    return member_logins


def fetch_all_invitations(org):
    """
    Fetches all pending invitations in the organization.

    Args:
        org: GitHub organization object.

    Returns:
        set: A set of invited email addresses.
    """
    invited_emails = set()
    try:
        for invitation in org.invitations():
            if invitation.email:
                invited_emails.add(invitation.email)
        logger.info(f"Fetched {len(invited_emails)} pending invitations.")
    except GithubException as e:
        logger.error(f"Error fetching invitations: {e}")
    return invited_emails


def invite_users(org, emails, invited_emails):
    """Invites users to the organization if they are not already invited."""
    success_count = 0
    failure_count = 0

    for email in emails:
        if email in invited_emails:
            logger.warning(f"Already invited: {email}")
            continue

        try:
            org.invite_user(email=email)
            logger.info(f"Invitation sent to {email}")
            success_count += 1
        except RateLimitExceededException:
            logger.error("Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(60)
            continue
        except GithubException as e:
            if e.status == 422:
                if 'rate' in e.args[1]['errors'][0]['message']:
                    logger.error(e.args[1]['errors'][0])
                    logger.info(f"Process aborted. Success: {success_count}, Failures: {failure_count}")
                    return
                else:
                    logger.warning(f"Cannot invite {email}: Already a member.")
            else:
                logger.error(f"Failed to invite {email}: {e}")
            failure_count += 1

        # Add delay to prevent hitting rate limits
        time.sleep(1)

    logger.info(f"Process completed. Success: {success_count}, Failures: {failure_count}")


def main():
    """Main function to read emails and invite users."""
    try:
        org = g.get_organization(org_name)
        logger.info(f"Successfully retrieved organization: {org_name}")
    except GithubException as e:
        logger.error(f"Error accessing organization: {e.data.get('message', 'Unknown error')}")
        sys.exit(1)

    invited_emails = fetch_all_invitations(org)
    emails = read_emails_from_csv(csv_file_path)
    invite_users(org, emails, invited_emails)


if __name__ == "__main__":
    main()
