import json
import prompty
from pathlib import Path
import requests, os, random
# to use the azure invoker make 
# sure to install prompty like this:
# pip install prompty[azure]
import prompty.azure
from prompty.tracer import trace, Tracer, console_tracer, PromptyTracer

import schedule
import time

# Keep dotenv for any other environment variables we might need
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
    
# Use local tags.json file
TAGS_FILE_PATH = "tags.json"

def load_tags_from_file():
    """Load tags from the local tags.json file."""
    try:
        with open(TAGS_FILE_PATH, 'r') as f:
            data = json.load(f)
        
        # Extract tag names from the data structure
        if isinstance(data, dict) and "tags" in data:
            # Format: {"tags": [{"name": "bug", "description": "..."}, ...]}
            return [tag["name"] for tag in data["tags"]]
        elif isinstance(data, list):
            # Format: ["bug", "enhancement", ...]
            return data
        else:
            print("⚠️ Unexpected tags.json format")
            return []
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"⚠️ Error loading tags.json: {e}")
        return []

def query_azure_search(query_text):
    """Load tags from file and return empty documents list (for compatibility)."""
    # No document search is performed now, just returning an empty list
    documents = []
    
    # Load tags from the local file
    tags = load_tags_from_file()
    
    # Return documents and tags (to maintain compatibility with existing code)
    return documents, tags

    return documents, unique_tags

@trace
def run_with_rag(title, description):
    """Run Prompty with RAG integration and return a Python list of tags."""
    # Load tags from local file
    _, tags = query_azure_search(description)
    
    # No need to augment description since we're not getting search results
    # Just use the original description
    
    # Execute the Prompty file
    raw = prompty.execute(
        "basic.prompty",
        inputs={
            "title": title,
            "tags": tags,
            "description": description
        }
    )

    # parse prompty’s JSON output
    try:
        parsed = json.loads(raw)
        # if your prompty returns a bare list:
        if isinstance(parsed, list):
            return parsed
        # if it returns {"tags": [...]}:
        if isinstance(parsed, dict):
            return parsed.get("tags", [])
    except json.JSONDecodeError:
        print("⚠️  Could not parse RAG output:", raw)

    return []

def fetch_unlabeled_issues(repo_url):
    """Fetch open issues that have no labels yet."""
    api_url = f"https://api.github.com/repos/{repo_url}/issues?state=open"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    resp = requests.get(api_url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch issues: {resp.status_code}")
        return []
    issues = resp.json()
    # only keep issues with an empty labels array
    return [i for i in issues if not i.get("labels")]

def label_issue(repo_url, issue_number, labels):
    """Apply the given labels to a GitHub issue."""
    if not labels:
        print(f"⏭️  No labels for #{issue_number}, skipping.")
        return

    api_url = f"https://api.github.com/repos/{repo_url}/issues/{issue_number}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    resp = requests.patch(api_url, headers=headers, json={"labels": labels})

    if resp.status_code == 200:
        print(f"✅  Labeled issue #{issue_number} with {labels}")
    else:
        print(f"❌  Failed to label issue #{issue_number}: {resp.status_code}")
        print("GitHub returned:", resp.json())

def process_issues():
    repo = "bethanyjep/build-your-first-agent"
    issues = fetch_unlabeled_issues(repo)
    for issue in issues:
        title = issue.get("title", "")
        body = issue.get("body", "")
        tags = run_with_rag(title, body)
        if tags:
            label_issue(repo, issue["number"], tags)

if __name__ == "__main__":
    # run every 1 minutes
    schedule.every(1).minutes.do(process_issues)
    print("Agent started: checking for new issues every minute.")
    while True:
        schedule.run_pending()
        time.sleep(1)