#!/usr/bin/env python3
"""
Script to fetch all hidden teams in a GitHub organization and change them to public.
Requires a GitHub personal access token with admin:org permissions.

You can edit the default_org and default_token variables in the main() function 
instead of passing them as command-line arguments each time.
"""

import requests
import argparse
import sys
import time


def get_all_teams(org, token):
    """Fetch all teams from a GitHub organization, including hidden ones."""
    all_teams = []
    page = 1
    per_page = 100
    
    while True:
        url = f"https://api.github.com/orgs/{org}/teams"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        params = {
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching teams: {response.status_code}")
            print(response.json())
            sys.exit(1)
        
        teams_page = response.json()
        if not teams_page:
            break
            
        all_teams.extend(teams_page)
        page += 1
        
        # Respect GitHub API rate limits
        if page > 1:
            time.sleep(0.5)
    
    return all_teams


def is_team_hidden(team):
    """Check if a team is hidden (privacy: 'secret')."""
    return team.get("privacy") == "secret"


def make_team_public(org, team_slug, token):
    """Change a team's visibility to public."""
    url = f"https://api.github.com/orgs/{org}/teams/{team_slug}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "privacy": "closed"
    }
    
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"Error updating team {team_slug}: {response.status_code}")
        print(response.json())
        return False
    
    return True


def main():
    # Default values (replace these with your actual values)
    default_org = "ewfx"  # Replace with your organization name
    default_token = "xx"     # Replace with your GitHub token
    
    parser = argparse.ArgumentParser(description="Change hidden GitHub teams to public")
    parser.add_argument("--org", help="GitHub organization name")
    parser.add_argument("--token", help="GitHub personal access token with admin:org permissions")
    parser.add_argument("--dry-run", action="store_true", help="List hidden teams without changing them")
    args = parser.parse_args()
    
    # Use command line arguments if provided, otherwise use defaults
    org = args.org if args.org else default_org
    token = args.token if args.token else default_token
    
    print(f"Fetching teams for organization: {org}")
    all_teams = get_all_teams(org, token)
    
    hidden_teams = [team for team in all_teams if is_team_hidden(team)]
    
    print(f"Found {len(all_teams)} total teams, {len(hidden_teams)} are hidden")
    
    if not hidden_teams:
        print("No hidden teams found.")
        return
    
    print("\nHidden teams:")
    for team in hidden_teams:
        print(f" - {team['name']} (slug: {team['slug']})")
    
    if args.dry_run:
        print("\nDry run mode - no changes were made")
        return
        
    # Confirmation prompt
    confirmation = input("\nDo you want to change these teams to public? (y/n): ").lower()
    if confirmation != 'y' and confirmation != 'yes':
        print("Operation cancelled.")
        return
    
    print("\nChanging visibility of hidden teams to public...")
    
    success_count = 0
    for team in hidden_teams:
        team_name = team['name']
        team_slug = team['slug']
        
        print(f"Updating {team_name}... ", end="")
        if make_team_public(org, team_slug, token):
            print("SUCCESS")
            success_count += 1
        else:
            print("FAILED")
        
        # Respect GitHub API rate limits
        time.sleep(0.5)
    
    print(f"\nCompleted. Changed {success_count} out of {len(hidden_teams)} teams to public visibility.")


if __name__ == "__main__":
    main()