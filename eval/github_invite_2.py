import csv
from github import Github
from github.GithubException import GithubException

# Personal Access Token (with admin:org permissions)
access_token = "xx"
# Organization name
org_name = "ewfx"
# Path to the CSV file containing the emails
csv_file_path = "Unique_Emails_Final_Set.csv"

# Initialize Github object
g = Github(access_token)

# Function to read emails from CSV file
def read_emails_from_csv(file_path):
    emails = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            emails.append(row['email'])
    return emails

try:
    # Get the organization object
    org = g.get_organization(org_name)

    # Get the list of all members in the organization
    members = org.get_members()
    member_emails = [member.email for member in members if member.email]

    # Get the list of all pending invitations
    invitations = org.invitations()
    invited_emails = [invitation.email for invitation in invitations]

    # Read emails from the CSV file
    emails = read_emails_from_csv(csv_file_path)
    
    # Invite users via email
    for email in emails:
        if email in member_emails:
            print(f"{email} is already a member of the organization.")
        elif email in invited_emails:
            print(f"An invitation has already been sent to {email}.")
        else:
            try:
                org.invite_user(email=email)
                print(f"Invitation sent to {email}")
            except GithubException as e:
                if e.status == 422:
                    if 'rate' in e.args[1]['errors'][0]['message']:
                        exit("API rate limit exceeded. Please try again later.")
                    else:
                        print(f"Lost an invite on {email}: Already a member.")
                else:
                    print(f"Failed to invite {email}: {e}")

except GithubException as e:
    print(f"Error accessing organization: {e.data['message']}")