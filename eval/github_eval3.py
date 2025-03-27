import datetime
import os
import shutil
import subprocess
from github import Github
from dotenv import load_dotenv
from git import Repo
from pytz import timezone
import stat
import csv  # Import the csv module

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
    cutoff = tz.localize(datetime.datetime(2025, 3, 27, 9, 0, 0))
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
    result = subprocess.run(['grep', '-r', 'SECRET_KEY', repo_path],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        "code": ["src", "test"]  # Added src and test as required subfolders
    }

    for root_dir, sub_dirs in expected_structure.items():
        root_path = os.path.join(repo_path, root_dir)
        if not os.path.isdir(root_path):
            return False
        for sub_dir in sub_dirs:
            if not os.path.isdir(os.path.join(root_path, sub_dir)):
                return False
    return True

def check_readme_edits(github_repo):
    """Checks if the README.md file has been edited at least twice."""
    readme_commits = [commit for commit in github_repo.get_commits(path='README.md')]
    return len(list(readme_commits)) >= 2

def check_readme_lines_added(github_repo):
    """Checks if the README.md file has more than 10 lines added in the last commit."""
    readme_commits = list(github_repo.get_commits(path='README.md'))
    if len(readme_commits) < 2:
        return False

    # Get the last two commits to the README.md
    last_commit = readme_commits[0]
    previous_commit = readme_commits[-1]

    try:
        comparison = github_repo.compare(previous_commit.sha, last_commit.sha)
        for file in comparison.files:
            if file.filename == 'README.md':
                return file.additions > 10
        return False  # README.md not found in the comparison (shouldn't happen if commits exist)
    except Exception as e:
        print(f"Error comparing commits for README.md: {e}")
        return False

def check_demo_video_or_presentation(repo_path):
    """Checks for the presence of a video file or presentation in artifacts/demo."""
    demo_path = os.path.join(repo_path, "artifacts", "demo")
    if not os.path.isdir(demo_path):
        return False  # artifacts/demo folder does not exist

    for filename in os.listdir(demo_path):
        if filename.lower() != "readme.md":
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.ppt', '.pptx', '.pdf')):
                return True  # Found a video or presentation file
    return False

def check_arch_document(repo_path):
    """Checks for a document (Word, PDF, or MD) in artifacts/arch."""
    arch_path = os.path.join(repo_path, "artifacts", "arch")
    if not os.path.isdir(arch_path):
        return False  # artifacts/arch folder does not exist

    for filename in os.listdir(arch_path):
        if filename.lower() != "readme.md":
            if filename.lower().endswith(('.doc', '.docx', '.pdf', '.md')):
                return True  # Found a document file
    return False

def check_code_subfolder_for_non_md(repo_path, subfolder):
    """
    Checks if a subfolder within the 'code' folder contains files other than .md.
    Args:
        repo_path: Path to the local repository.
        subfolder: Name of the subfolder to check (e.g., 'src', 'test').
    Returns:
        True if the subfolder contains at least one file that is not a .md file, False otherwise.
    """
    folder_path = os.path.join(repo_path, "code", subfolder)
    if not os.path.isdir(folder_path):
        return False  # The folder does not exist

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(('.md')):
            return True  # Found a file that is not .md
    return False

def check_repo(repo_path, github_repo):
    checks = {
        "Programming Languages": guess_language(github_repo),
        "README.md exists": check_file_exists(repo_path, "README.md"),
        "README.md edited at least 2 times": check_readme_edits(github_repo),
        "README.md lines added": check_readme_lines_added(github_repo),
        "Total LOC": calculate_loc(repo_path),
        "Folder structure is correct": check_folder_structure(repo_path),
        "Total Commits": count_commits(github_repo),
        "Commits after cutoff": check_commits_after_cutoff(github_repo),
        "Demo video/presentation exists": check_demo_video_or_presentation(repo_path),
        "Arch document exists": check_arch_document(repo_path),
        "Code src has non-md files": check_code_subfolder_for_non_md(repo_path, "src"),
        "Code test has non-md files": check_code_subfolder_for_non_md(repo_path, "test"),
    }
    return checks


def print_results(repo, checks):
    """Prints the results of the repository checks, including the actual values."""
    print(f"Results for repository: {repo.full_name}")
    for check, result in checks.items():
        if check == "Total LOC":
            print(f"{check}: {result} lines")
        elif check == "Programming Languages":
            print(f"{check}: {result}")  # Print the language name
        else:
            print(f"{check}: {result}") # print the boolean value
    print("\n")



def remove_readonly(func, path, excinfo):
    # Change the file to be writable and try again
    os.chmod(path, stat.S_IWRITE)
    func(path)


def main():
    # Load .env file
    load_dotenv()
    github_token = "xx"
    g = Github(github_token)

    org_name = 'ewfx'
    base_path = 'repo/target'
    csv_filename = 'repo_evaluation_results.csv'  # Define the CSV filename
    repo_list_csv = 'ewfx_repos_with_commits_20250326_152856.csv' # Define the CSV file containing the list of repos

    org = g.get_organization(org_name)

    # Prepare the CSV file
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        header = ['Repository Name', 'Programming Languages', 'README.md exists',
                  'README.md edited at least 2 times', 'README.md lines added',
                  'Total LOC', 'Folder structure is correct', 'Total Commits',
                  'Commits after cutoff', 'Demo video/presentation exists',
                  'Arch document exists', 'Code src has non-md files',
                  'Code test has non-md files', 'Score']
        writer.writerow(header)

        # Read the list of repositories from the CSV file
        try:
            with open(repo_list_csv, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                repo_names = [row['repo_name'] for row in reader]  # Assuming the column name is 'repo'
        except FileNotFoundError:
            print(f"Error: File not found: {repo_list_csv}")
            return
        except KeyError:
            print(f"Error: Column 'repo' not found in CSV file: {repo_list_csv}")
            return
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return

        for repo_name in repo_names:
            try:
                # Get the repository object by name
                repo = org.get_repo(repo_name)
                print(f"Processing: {repo.full_name}")

                if repo.archived:
                    continue

                local_path = base_path + '/' + repo.name

                if os.path.exists(local_path):
                    shutil.rmtree(local_path, onerror=remove_readonly)

                # Use a shallow clone to avoid downloading the entire history and large files
                Repo.clone_from(repo.ssh_url, local_path, depth=1)
                checks = check_repo(local_path, repo)
                print_results(repo, checks)  # Keep printing results

                # Calculate the score
                score = calculate_score(checks)

                # Write results to CSV file
                row = [repo.full_name] + [str(checks[check]) for check in header[1:-1]] + [score]
                writer.writerow(row)

            except Exception as e:
                print(f"Error processing repository {repo_name}: {e}")
            finally:
                if os.path.exists(local_path):
                    shutil.rmtree(local_path, onerror=remove_readonly)

    print(f"Results written to {csv_filename}")  # Print message after writing to CSV



if __name__ == "__main__":
    main()
