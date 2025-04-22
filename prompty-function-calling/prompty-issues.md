# GitHub Issue Tagging Agent with Prompty

## Goal
Create an intelligent Prompty agent that listens for new GitHub issues and automatically assigns appropriate tags and categories using natural language understanding.

## What It Does
- Loops through existing issues in a repo (open or closed)
- Sends each issue (title + body) to a Prompty asset
- Receives suggested tags
- Applies those tags using the GitHub API