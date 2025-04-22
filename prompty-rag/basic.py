import json
import prompty
from pathlib import Path
import requests, os, random
# to use the azure invoker make 
# sure to install prompty like this:
# pip install prompty[azure]
import prompty.azure
from prompty.tracer import trace, Tracer, console_tracer, PromptyTracer
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
    """Run Prompty with RAG integration."""
    # Query Azure Cognitive Search
    search_results, tags = query_azure_search(description)

    # Combine search results with the original description
    augmented_description = description + "\n\n" + "\n".join(search_results)

    # Execute the Prompty file
    result = prompty.execute(
        "basic.prompty",
        inputs={
            "title": title,
            "tags": tags,
            "description": augmented_description
        }
    )

    return result

if __name__ == "__main__":
    base = Path(__file__).parent

    # Fetch a random issue from GitHub
    repo_url = "bethanyjep/build-your-first-agent"  # Replace with your GitHub repository
    issue = fetch_github_issues(repo_url)
    if not issue:
        print("No issue to process.")
        exit()

    # Extract title and description from the random issue
    title = issue.get("title", "No Title")
    description = issue.get("body", "No Description")

    # Categorize the issue
    result = run_with_rag(title, description)
    

    # Print the results
    print(f"Issue: {title}")
    print(f"Description: {description}")
    print(f"Categorized Tags: {result}")
    print("-" * 50)