# GitHub Agent

The GitHub Agent provides a natural language interface for interacting with GitHub repositories, pull requests, issues, and code.

## Features

- List and view GitHub pull requests and issues
- Find connections between PRs and issues (e.g., which issues will be closed by a PR)
- Search code in repositories
- Clone repositories for deeper analysis
- Examine commit history, including finding the commit before a PR was created
- Track repository status and changes

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- Git installed

## Usage

### CLI Mode

```bash
# Start the GitHub agent in UI mode
aurelian github --ui

# Make a direct query to the agent
aurelian github "List open PRs in monarch-initiative/aurelian"

# Clone a repository
aurelian github "Clone the repository obophenotype/cell-ontology"
```

### Direct Tool Usage

For more direct control, you can use the GitHub CLI commands:

```bash
# Clone a repository
aurelian github-cli clone obophenotype/cell-ontology

# List pull requests
aurelian github-cli list-prs --repo monarch-initiative/aurelian

# View a specific pull request
aurelian github-cli view-pr 31 --repo monarch-initiative/aurelian

# Get the commit before a PR was created
aurelian github-cli commit-before-pr 31 --repo monarch-initiative/aurelian

# Search code in a repository
aurelian github-cli search "RunContext" --repo monarch-initiative/aurelian

# Start an interactive chat with the GitHub agent
aurelian github-cli chat
```

## Example Queries

- "List the open pull requests in monarch-initiative/aurelian"
- "What issues will be closed by PR #31?"
- "What was the commit before PR #31 was created?"
- "Search for code related to 'RunContext' in the repository"
- "Clone the repository obophenotype/cell-ontology and tell me about its structure"
- "Show me the most recent commits to the main branch"