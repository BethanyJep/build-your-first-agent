import json
import prompty
from pathlib import Path
import requests, os, random
# to use the azure invoker make 
# sure to install prompty like this:
# pip install prompty[azure]
import prompty.azure
from prompty.tracer import trace, Tracer, console_tracer, PromptyTracer
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# add console and json tracer:
# this only has to be done once
# at application startup
Tracer.add("console", console_tracer)
json_tracer = PromptyTracer()
Tracer.add("PromptyTracer", json_tracer.tracer)

# GitHub API settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # Add your GitHub token here

def fetch_github_issues(repo_url):
    """Fetch issues from the specified GitHub repository."""
    api_url = f"https://api.github.com/repos/{repo_url}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        issues = response.json()
        if not issues:
            print("No issues found in the repository.")
            return None
        return random.choice(issues)  # Pick a random issue
    else:
        print(f"Failed to fetch issues: {response.status_code} - {response.text}")
        return None

@trace
def run(    
      title: any,
      tags: any,
      description: any
) -> str:

  # execute the prompty file
  result = prompty.execute(
    "basic.prompty", 
    inputs={
      "title": title,
      "tags": tags,
      "description": description
    }
  )

  return result

if __name__ == "__main__":
    base = Path(__file__).parent

    # Fetch a random issue from GitHub
    repo_url = "BethanyJep/build-your-first-agent"  # Replace with your GitHub repository
    issue = fetch_github_issues(repo_url)
    if not issue:
        print("No issue to process.")
        exit()

    # Extract title and description from the random issue
    title = issue.get("title", "No Title")
    description = issue.get("body", "No Description")

    # Load tags from tags.json
    tags = json.loads(Path(base, "tags.json").read_text())

    # Categorize the issue
    result = run(title, tags, description)

    # Print the results
    print(f"Issue: {title}")
    print(f"Description: {description}")
    print(f"Categorized Tags: {result}")
    print("-" * 50)
