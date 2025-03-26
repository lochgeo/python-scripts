import csv
import logging
import time
import os
import sys
from github import Github
from github.GithubException import GithubException

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

# Personal Access Token (with admin:org permissions)
access_token = "xx"
# Organization name
org_name = "ewfx"
# Path to the CSV file containing the emails
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
    """
    Reads email addresses from a CSV file.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        list: A list of email addresses.
    """
    emails = []
    try:
        with open(file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                emails.append(row["email"])
        logger.info(f"Successfully read {len(emails)} emails from CSV file.")
    except FileNotFoundError:
        logger.error(f"CSV file not found at path: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        sys.exit(1)
    return emails


def fetch_all_members(org):
    """
    Fetches all members of the organization using pagination.

    Args:
        org: GitHub organization object.

    Returns:
        set: A set of member login names (usernames).
    """
    member_logins = set()
    try:
        for member in org.get_members():
            member_logins.add(member.login)  # Use login instead of email
        logger.info(f"Fetched {len(member_logins)} members.")
    except GithubException as e:
        logger.error(f"Error fetching members: {e}")
    return member_logins


def fetch_all_invitations(org):
    """
    Fetches all pending invitations in the organization using pagination.

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


def invite_users(org, emails, member_logins, invited_emails):
    """
    Invites users to the organization if they are not already members or invited.

    Args:
        org: GitHub organization object.
        emails (list): List of email addresses to invite.
        member_logins (set): Set of current member login names (usernames).
        invited_emails (set): Set of pending invitation emails.
    """
    success_count = 0
    failure_count = 0

    for email in emails:
        # Check if the email is already invited
        if email in invited_emails:
            logger.info(f"An invitation has already been sent to {email}.")
            continue

        # Check if the user is already a member (by login name)
        try:
            user = g.get_user(email)
            if user.login in member_logins:
                logger.info(f"{email} is already a member of the organization.")
                continue
        except GithubException as e:
            logger.error(f"Failed to fetch user for {email}: {e}")
            failure_count += 1
            continue

        # Send invitation
        try:
            org.invite_user(email=email)
            logger.info(f"Invitation sent to {email}")
            success_count += 1
        except GithubException as e:
            logger.error(f"Failed to invite {email}: {e}")
            failure_count += 1

        # Add a delay to avoid hitting rate limits
        time.sleep(1)  # 1 second delay between API calls

    logger.info(f"Process completed. Success: {success_count}, Failures: {failure_count}")


def main():
    """Main function to read emails and invite users."""
    try:
        # Get the organization object
        org = g.get_organization(org_name)
        logger.info(f"Successfully retrieved organization: {org_name}")
    except GithubException as e:
        logger.error(f"Error accessing organization: {e.data['message']}")
        sys.exit(1)

    # Fetch all members and invitations
    member_logins = fetch_all_members(org)
    invited_emails = fetch_all_invitations(org)

    # Read emails from the CSV file
    emails = read_emails_from_csv(csv_file_path)

    # Invite users
    invite_users(org, emails, member_logins, invited_emails)


if __name__ == "__main__":
    main()