import os
import csv
from io import StringIO
from typing import List, Optional, Dict
from pathlib import Path
import google.generativeai as genai  # Import the Gemini API library
import git  # Import GitPython

# ===============================
# Configuration
# ===============================

# Replace with your actual GitHub organization name.
GITHUB_ORGANIZATION = "your-github-organization"
# Path to the CSV file containing the list of repositories.
REPO_LIST_CSV = "repos.csv"

LLM_API_KEY = "YOUR_GEMINI_API_KEY" 
CLONE_BASE_DIR = "cloned_repos"

# LLM prompt
LLM_PROMPT = """
Evaluate the quality of the following submission for a hackathon.
Consider the following criteria:

- Completeness: Does the submission fulfill the requirements of the hackathon?
- Innovation: How novel and creative is the submission?
- Technical Difficulty: How complex and challenging is the technology used?
- Presentation: How well is the submission presented and documented?

Provide a score from 1 to 10 (1 being the lowest, 10 being the highest) for each criterion.
Return the result as a CSV string with the header:
Completeness,Innovation,Technical Difficulty,Presentation

Do not include any explanation or other text.
Only return the CSV data.

Submission text:
{submission_text}
"""

# Output CSV file.
OUTPUT_CSV_FILE = "evaluation_results.csv"

# Configure the Gemini API
genai.configure(api_key=LLM_API_KEY)
MODEL_NAME = 'gemini-pro'  # Specify the Gemini Pro model


# ===============================
# Helper Functions
# ===============================


def read_repo_list(csv_file: str) -> List[str]:
    """
    Reads the list of repositories from a CSV file.

    Args:
        csv_file (str): The path to the CSV file.  The CSV should contain
                        a header row, and a column named "repo_name".

    Returns:
        List[str]: A list of repository names.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        KeyError: If the CSV file does not contain a "repo_name" column.
        csv.Error: If there is an error reading the CSV file.
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if "repo_name" not in reader.fieldnames:
                raise KeyError(
                    "CSV file must contain a column named 'repo_name'")
            repo_names = [row["repo_name"] for row in reader]
            return repo_names
    except FileNotFoundError as e:
        print(f"Error: File not found: {csv_file}")
        raise e
    except KeyError as e:
        print(f"Error: {e}")
        raise e
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e


def clone_repo(repo_name: str, clone_dir: str) -> Optional[Path]:
    """
    Clones a repository from GitHub using GitPython.

    Args:
        repo_name (str): The name of the repository to clone.
        clone_dir (str): The directory where the repository should be cloned.

    Returns:
        Optional[Path]: The path to the cloned repository, or None on error.
    """
    repo_url = f"https://github.com/{GITHUB_ORGANIZATION}/{repo_name}.git"
    destination = Path(clone_dir) / repo_name
    try:
        # Check if the directory already exists
        if destination.exists():
            print(
                f"Repository {repo_name} already exists at {destination}. Skipping cloning.")
            return destination

        # Use GitPython to clone the repository.
        git.Repo.clone_from(repo_url, str(destination))
        print(f"Successfully cloned {repo_name} to {destination}")
        return destination
    except git.GitCommandError as e:
        print(f"Error cloning repository {repo_name}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while cloning {repo_name}: {e}")
        return None


def concatenate_text_files(repo_path: Path) -> str:
    """
    Concatenates all text files in a directory and its subdirectories.
    Skips binary, video, pdf, and ppt files.

    Args:
        repo_path (Path): The path to the repository directory.

    Returns:
        str: The concatenated text content, or an empty string if no
             text files are found or an error occurs.
    """
    text_content = StringIO()
    # List of file extensions to exclude
    exclude_extensions = {
        '.bin', '.exe', '.dll',  # Binary
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',  # Images
        '.mp4', '.avi', '.mov', '.wmv',  # Video
        '.mp3', '.wav', '.ogg',  # Audio
        '.pdf', '.doc', '.docx', '.rtf',  # Documents
        '.ppt', '.pptx', '.odp',  # Presentations
        '.zip', '.rar', '.gz', '.tar', '.7z',  # Archives
        '.iso',  # Disk Images
        '.pyc',  # Python compiled files
        '.class',  # Java class files
        '.jar',  # Java Archive
    }

    try:
        for root, _, files in os.walk(repo_path):
            for file in files:
                file_path = Path(root) / file
                if not any(file.lower().endswith(ext) for ext in exclude_extensions):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text_content.write(f.read())
                            text_content.write("\n\n")  # Add separators
                    except UnicodeDecodeError:
                        print(f"Skipping non-text file: {file_path}")
                    except Exception as e:
                        print(
                            f"Error reading file {file_path}: {e}. Skipping.")
        return text_content.getvalue()
    except Exception as e:
        print(f"An error occurred while concatenating files: {e}")
        return ""  # Return empty string on error


def evaluate_submission(submission_text: str) -> Optional[Dict[str, int]]:
    """
    Evaluates the submission text using the Gemini Pro LLM.

    Args:
        submission_text (str): The text of the submission to evaluate.

    Returns:
        Optional[Dict[str, int]]: The LLM's evaluation as a dictionary
                                  {"Completeness": score, "Innovation": score, ...},
                                  or None on error.
    """
    # Import the Gemini API
    import google.generativeai as genai

    if not submission_text:
        print("Warning: No submission text to evaluate.")
        return None

    prompt = LLM_PROMPT.format(submission_text=submission_text)

    try:
        model = genai.GenerativeModel(MODEL_NAME)  # Use the configured model
        response = model.generate_content(prompt)
        llm_response = response.text.strip()  # Get the text and remove extra spaces

        # Parse the CSV output from the LLM
        reader = csv.reader(StringIO(llm_response))
        scores_list = next(reader)  # Get the first row of scores
        scores = [int(s) for s in scores_list]  # convert scores to integers

        # Construct the result dictionary
        evaluation_result = {
            "Completeness": scores[0],
            "Innovation": scores[1],
            "Technical Difficulty": scores[2],
            "Presentation": scores[3],
        }
        return evaluation_result
    except Exception as e:
        print(f"Error communicating with LLM API: {e}")
        print(f"Error details: {e}")
        return None



def main():
    """
    Main function to run the script.
    """
    # Create the clone directory if it doesn't exist
    os.makedirs(CLONE_BASE_DIR, exist_ok=True)

    try:
        repo_list = read_repo_list(REPO_LIST_CSV)
    except Exception as e:
        print(f"Failed to read repository list: {e}")
        return  # Exit if we can't read the repo list

    # Prepare the output CSV file
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        writer.writerow(
            ["Repository Name", "Completeness", "Innovation",
             "Technical Difficulty", "Presentation"]
        )

        for repo_name in repo_list:
            print(f"Processing repository: {repo_name}")
            repo_path = clone_repo(repo_name, CLONE_BASE_DIR)
            if repo_path:  # Only proceed if cloning was successful
                submission_text = concatenate_text_files(repo_path)
                if submission_text:
                    evaluation = evaluate_submission(submission_text)
                    if evaluation:
                        # Write the results to the CSV file
                        writer.writerow(
                            [repo_name] + [evaluation[criterion] for criterion in [
                                "Completeness", "Innovation",
                                "Technical Difficulty", "Presentation"
                            ]]
                        )
                        print(
                            f"Evaluation for {repo_name} written to {OUTPUT_CSV_FILE}")
                    else:
                        print(
                            f"Failed to evaluate submission for {repo_name}.")
                        writer.writerow(
                            [repo_name, "N/A", "N/A", "N/A", "N/A"])  # Write N/A
                else:
                    print(f"No text files found in {repo_name}.")
                    writer.writerow(
                        [repo_name, "No Text", "No Text", "No Text", "No Text"])
            else:
                print(f"Failed to clone {repo_name}. Skipping evaluation.")
                writer.writerow([repo_name, "Clone Failed",
                                 "Clone Failed", "Clone Failed", "Clone Failed"])


if __name__ == "__main__":
    main()

