import datetime
import os
import shutil
import subprocess
from github import Github
from dotenv import load_dotenv
from git import Repo
from pytz import timezone
import stat

def calculate_score(checks):
    total_checks = len(checks)
    passed_checks = sum(1 for check in checks.values() if check)
    return (passed_checks / total_checks) * 100

def guess_language(repo):
    languages = repo.get_languages()
    return list(languages.keys())[0] if languages else None

def count_commits(repo):
    commits = repo.get_commits()
    return len(list(commits))

def check_commits_after_cutoff(repo):
    tz = timezone('Asia/Kolkata')
    cutoff = tz.localize(datetime.datetime(2024,10,19,9,0,0))
    commits = repo.get_commits()

    for commit in commits:
        localtime = commit.commit.author.date.astimezone(tz)
        if localtime > cutoff:
            print(f"Commit SHA : {commit.sha}")
            print(f"Author : {commit.commit.author.name}")
            print(f"Date: {commit.commit.author.date}")
            print(f"Message: {commit.commit.message}")  
            return False
    
    return True

def check_file_exists(repo_path, filename):
    return os.path.isfile(os.path.join(repo_path, filename))

def check_dir_exists(repo_path, dirname):
    return os.path.isdir(os.path.join(repo_path, dirname))

def check_for_secrets(repo_path):
    result = subprocess.run(['grep', '-r', 'SECRET_KEY', repo_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def calculate_loc(repo_path):
    total_loc = 0
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_loc += sum(1 for _ in f)
            except (UnicodeDecodeError, FileNotFoundError):
                pass  # Skip files that can't be read
    return total_loc

def check_folder_structure(repo_path):
    expected_structure = {
        "artifacts": ["demo"],
        "code": []
    }
    
    for root_dir, sub_dirs in expected_structure.items():
        root_path = os.path.join(repo_path, root_dir)
        if not os.path.isdir(root_path):
            return False
        for sub_dir in sub_dirs:
            if not os.path.isdir(os.path.join(root_path, sub_dir)):
                return False
    return True

def check_repo(repo_path, github_repo):
    checks = {
        "Programming Languages" : guess_language(github_repo),
        "README.md exists": check_file_exists(repo_path, "README.md"),
        "Total LOC": calculate_loc(repo_path),
        "Folder structure is correct": check_folder_structure(repo_path),
        "Total Commits": count_commits(github_repo),
        "Commits after cutoff": check_commits_after_cutoff(github_repo)
    }
    return checks

def print_results(repo, checks):
    print(f"Results for repository: {repo.full_name}")
    for check, result in checks.items():
        if check == "Total LOC":
            print(f"{check}: {result} lines")
        else:
            print(f"{check}: {'PASSED' if result else 'FAILED'}")
    print("\n")

def remove_readonly(func, path, excinfo):
    # Change the file to be writable and try again
    os.chmod(path, stat.S_IWRITE)
    func(path)
    
def main():
    # Load .env file
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    g = Github(github_token)

    org_name = 'nitkhackathon2024'
    base_path = 'repo/target'

    org = g.get_organization(org_name)

    for repo in org.get_repos():
        print(f"Processing: {repo.full_name}")

        if repo.archived:
            continue

        local_path =  base_path + '/' + repo.name
        
        if os.path.exists(local_path):
            shutil.rmtree(local_path, onerror=remove_readonly)

        Repo.clone_from(repo.ssh_url, local_path)
        checks = check_repo(local_path, repo)
        print_results(repo, checks)
        shutil.rmtree(local_path, onerror=remove_readonly)

if __name__ == "__main__":
    main()
