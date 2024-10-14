import os
import json
import requests
from bs4 import BeautifulSoup

# Load the JSON data
json_file_path = "Repos/HomeAssistantRepos.json"

with open(json_file_path, "r") as f:
    data = json.load(f)


# Create a directory for the documentation if it doesn't exist
# Iterate over each letter category in the repos
def create_repo_docs(data):
    if not os.path.exists("docs/repo_docs"):
        os.makedirs("docs/repo_docs")

    existing_files = set(os.listdir("docs/repo_docs"))
    skipped_repos = []  # List to track repos that were skipped

    for letter, repos in data.get("english_repos", {}).items():
        for repo in repos:
            author = repo["author"].replace(" ", "")
            repo_name = repo["name"].replace("'s Repo", "").replace(" ", "")
            filename = f"{author}_{repo_name}.md"

            # Avoid duplicates by checking if the file already exists
            if filename in existing_files:
                count = 1
                base_filename = filename.replace(".md", "")
                original_filename = filename
                while os.path.exists(f"docs/repo_docs/{filename}"):
                    filename = f"{base_filename}_{count}.md"
                    count += 1
                skipped_repos.append(original_filename)
                continue

            # Add the new filename to the set
            existing_files.add(filename)
            write_repo_doc(filename, repo)

    return skipped_repos


# Function to write the documentation for each repo
def write_repo_doc(filename, repo):
    with open(f"docs/repo_docs/{filename}", "w") as file:

        def fetch_readme_content(url):
            # Construct the URL to the README.md file
            readme_url = url.rstrip("/") + "/blob/main/README.md"
            response = requests.get(readme_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                readme_content = soup.find("article")
                return (
                    readme_content.get_text()
                    if readme_content
                    else "README.md content not found."
                )
            else:
                return "Failed to fetch README.md."

        readme_content = fetch_readme_content(repo["url"])
        file.write(f"# {repo['name']}\n\n")
        file.write(f"**Author**: {repo['author']}\n")
        file.write(f"**URL**: {repo['url']}\n")
        file.write(f"\n\n## README.md Content\n\n{readme_content}")


# Function to print the skipped repos
def print_skipped_repos(skipped_repos):
    if skipped_repos:
        print(
            "The following documentation files were skipped because they already exist:"
        )
        for repo in skipped_repos:
            print(repo)
    else:
        print("Documentation generation complete!")


# Main function to run the script
if __name__ == "__main__":
    skipped_repos = create_repo_docs(data)
    print_skipped_repos(skipped_repos)
    print("All documentation files were created successfully!")
