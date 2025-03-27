# Working with Azure AI Projects Agent

This guide explains how to create and interact with an AI agent using Azure AI Projects SDK.

## Setup and Prerequisites

### Required Environment Variables
- `MODEL_DEPLOYMENT`
- `PROJECT_CONNECTION`
- `BING_CONNECTION_NAME`

### Required Python Packages
```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, BingGroundingTool, ToolSet
from azure.identity import DefaultAzureCredential
```

## Code Structure

### 1. Initialize Tools
```python
def initialize_tools():
    # Create bing grounding tool and toolset
```

### 2. Client Setup
```python
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(...),
    conn_str=os.getenv("PROJECT_CONNECTION")
)
```

### 3. Main Workflow
- Create an AI agent
- Create a conversation thread
- Add messages
- Run the agent
- Process responses

### 4. Handling Results
- Retrieve conversation messages
- Save generated images
- Process assistant responses

### 5. Cleanup
```python
project_client.agents.delete_agent(agent.id)
```

## Authentication

To resolve authentication issues:

1. Install Azure CLI:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

2. Login to Azure:
```bash
az login
```

3. Verify authentication:
```bash
az account show
```

## Generated Output
The script can generate:
- Text responses
- Charts and visualizations (saved as PNG files)
- Data analysis results

## Error Handling
- Checks for run failures
- Validates message responses
- Ensures proper cleanup of resources