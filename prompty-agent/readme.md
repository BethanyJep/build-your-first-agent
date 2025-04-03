# GitHub Issue Categorization

## Overview
The `categorize-issues` prompt is designed to automatically tag GitHub issues using a predefined list of tags. It leverages the Azure OpenAI GPT model to analyze issue titles and descriptions and return appropriate tags.

## Features
- Automatically categorizes GitHub issues based on their content.
- Supports a predefined list of tags loaded from `tags.json`.
- Ensures output is a valid JSON array of strings.
- Provides guidelines to ensure accurate tagging.

## Configuration
The prompt uses the following environment variables for Azure OpenAI configuration:
- `AZURE_OPENAI_ENDPOINT`: The Azure OpenAI endpoint.
- `AZURE_OPENAI_KEY`: The API key for Azure OpenAI.
- `AZURE_OPENAI_API_VERSION`: The API version to use.
- `tags.json`: A file containing the list of available tags.

## Prompt Structure
### System Message
The system message defines the assistant's behavior:
- Lists available tags dynamically from `tags.json`.
- Provides clear guidelines for selecting tags.

### User Input
The user provides:
- `Issue Title`: The title of the GitHub issue.
- `Issue Description`: A detailed description of the issue.

### Output
The assistant returns:
- A JSON array of strings representing the selected tags.
- If no tags apply, it returns: `["No tags apply to this issue. Please review the issue and try again."]`.

## Example
### Input
```json
{
  "title": "App crashes when running in Azure CLI",
  "description": "Running the generated code in Azure CLI throws a Python runtime error."
}
```

### Output
```json
["bug", "tool:cli", "runtime:python", "integration:azure"]
```

## Usage
- Create a virtual environment: ```python -m venv venv```
- Activate the virtual environment: ```source venv/bin/activate```
- Install the requirements: ```pip installl -r requirements.txt```
- Run the application using ```flask run```