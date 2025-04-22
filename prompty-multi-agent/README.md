# Project Overview

This project, `prompty-multi-agent`, is designed to automate the process of managing GitHub issues through a series of specialized agents. Each agent has a distinct role in the workflow, from fetching new issues to applying labels based on classification and evaluation.

## Agents

### 1. FetchAgent
- **File:** `agents/fetch-agent.prompty`
- **Functionality:** Responsible for pulling new issues from GitHub using function calling. It includes configurations and guidelines necessary for fetching issues.

### 2. ClassifyAgent
- **File:** `agents/classify-agent.prompty`
- **Functionality:** Reads issues and runs a Retrieval-Augmented Generation (RAG) process to emit the issue along with its associated tags. It specifies the classification criteria based on issue content.

### 3. EvaluatorAgent
- **File:** `agents/evaluator-agent.prompty`
- **Functionality:** Evaluates the labels assigned to issues to determine their appropriateness using a different model. It outlines the evaluation criteria and processes.

### 4. LabelAgent
- **File:** `agents/label-agent.prompty`
- **Functionality:** Reads the issue and its tags, interacting with GitHub to apply the labels. It includes configurations for communicating with the GitHub API.

## Orchestrator

- **File:** `src/orchestrator.ts`
- **Functionality:** Serves as the main orchestrator for the agents. It imports the agents and coordinates their interactions, ensuring a seamless workflow from fetching issues to labeling them.

## Configuration Files

- **File:** `package.json`
  - Contains the configuration for npm, listing dependencies and scripts needed for building or running the application.

- **File:** `tsconfig.json`
  - Specifies the compiler options and files to include in the TypeScript compilation process.

## Setup Instructions

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the necessary dependencies by running:
   ```
   npm install
   ```
4. Configure your environment variables for GitHub API access.
5. Run the orchestrator to start the workflow:
   ```
   npm start
   ```

## Contribution

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.