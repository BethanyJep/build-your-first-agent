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

from azure.search.documents import SearchClient
from azure.search.documents.models import (
    VectorizedQuery
)
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import QueryType
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
    
# Azure AI Search settings
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")  # Add your Azure Search endpoint
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")  # Add your Azure Search API key
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")  # Add your Azure Search index name

def query_azure_search(query_text):
    """Query Azure AI Search for relevant documents and tags."""
    search_client = SearchClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        index_name=SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )

    # Perform the search
    results = search_client.search(
        search_text=query_text,
        query_type=QueryType.SIMPLE,
        top=5  # Retrieve top 5 results
    )

    # Extract content and tags from results
    documents = [doc["content"] for doc in results]
    tags = [doc.get("tags", []) for doc in results]  # Assuming "tags" is a field in the index

    # Flatten and deduplicate tags
    unique_tags = list(set(tag for tag_list in tags for tag in tag_list))

    return documents, unique_tags

@trace
def run_with_rag(title, description):
    """Run Prompty with RAG integration and return a Python list of tags."""
    # Query Azure Cognitive Search
    search_results, azure_tags = query_azure_search(description)

    # Combine search results with the original description
    augmented_description = description + "\n\n" + "\n".join(search_results)

    # write out tags.json for basic.prompty to consume
    Path("tags.json").write_text(json.dumps(azure_tags))

    # Execute the Prompty file
    raw = prompty.execute(
        "basic.prompty",
        inputs={
            "title": title,
            "tags": azure_tags,
            "description": augmented_description
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
    # run every 5 minutes
    schedule.every(1).minutes.do(process_issues)
    print("Agent started: checking for new issues every minute.")
    while True:
        schedule.run_pending()
        time.sleep(1)