import os
import requests
import zipfile
import tempfile
import shutil
import subprocess
from github import Github
from dotenv import load_dotenv

def download_repo(g, repo_url):
    repo_name = '/'.join(repo_url.rstrip('/').split('/')[-2:])
    repo = g.get_repo(repo_name)
    download_url = repo.get_archive_link('zipball')
    response = requests.get(download_url)
    if response.status_code == 200:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"{repo_name.split('/')[-1]}.zip")
        with open(zip_path, 'wb') as zip_file:
            zip_file.write(response.content)
        return temp_dir, zip_path
    else:
        print(f"Failed to download repository {repo_url}")
        return None, None

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    extracted_folders = [os.path.join(extract_to, d) for d in os.listdir(extract_to) if os.path.isdir(os.path.join(extract_to, d))]
    return extracted_folders[0] if extracted_folders else None

def check_file_exists(repo_path, filename):
    return os.path.isfile(os.path.join(repo_path, filename))

def check_dir_exists(repo_path, dirname):
    return os.path.isdir(os.path.join(repo_path, dirname))

def check_for_secrets(repo_path):
    result = subprocess.run(['grep', '-r', 'SECRET_KEY', repo_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def run_linter(repo_path, linter_config_file):
    if check_file_exists(repo_path, linter_config_file):
        result = subprocess.run(['eslint', repo_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    return False

def run_tests(repo_path, test_dir):
    if check_dir_exists(repo_path, test_dir):
        result = subprocess.run(['pytest', test_dir], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    return False

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
        "artifacts": ["demo", "design"],
        "code": ["src", "test"]
    }
    
    for root_dir, sub_dirs in expected_structure.items():
        root_path = os.path.join(repo_path, root_dir)
        if not os.path.isdir(root_path):
            return False
        for sub_dir in sub_dirs:
            if not os.path.isdir(os.path.join(root_path, sub_dir)):
                return False
    return True

def check_repo(repo_path):
    checks = {
        "README.md exists": check_file_exists(repo_path, "README.md"),
        "LICENSE exists": check_file_exists(repo_path, "LICENSE"),
        "Linting configuration exists": check_file_exists(repo_path, ".eslintrc.json"),
        "Tests directory exists": check_dir_exists(repo_path, "tests"),
        "CI configuration exists": check_file_exists(repo_path, ".github/workflows/main.yml"),
        "package.json exists": check_file_exists(repo_path, "package.json"),
        "No hardcoded secrets": not check_for_secrets(repo_path),
        "Linting passes": run_linter(repo_path, ".eslintrc.json"),
        "Tests pass": run_tests(repo_path, "tests"),
        "Total LOC": calculate_loc(repo_path),
        "Folder structure is correct": check_folder_structure(repo_path)
    }
    return checks

def print_results(repo_url, checks):
    print(f"Results for repository: {repo_url}")
    for check, result in checks.items():
        if check == "Total LOC":
            print(f"{check}: {result} lines")
        else:
            print(f"{check}: {'PASSED' if result else 'FAILED'}")
    print("\n")

def main():
    # Load .env file
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    g = Github(github_token)

    repo_urls = [
        "https://github.com/user/repo1",
        "https://github.com/user/repo2"
    ]

    for repo_url in repo_urls:
        temp_dir, zip_path = download_repo(g, repo_url)
        if zip_path:
            repo_path = extract_zip(zip_path, temp_dir)
            if repo_path:
                checks = check_repo(repo_path)
                print_results(repo_url, checks)
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
