"""
Agent for working with GitHub repositories, issues, and pull requests.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

from pydantic_ai import Agent, Tool, RunContext

from aurelian.agents.github.github_config import GitHubDependencies
from aurelian.agents.github.github_tools import (
    list_pull_requests,
    view_pull_request,
    list_issues,
    view_issue,
    get_pr_closing_issues,
    get_commit_before_pr,
    search_code,
    clone_repository
)
from aurelian.agents.filesystem.filesystem_tools import inspect_file, list_files


class GitHubRepoSummary(BaseModel):
    """
    Summary of a GitHub repository.
    """
    repo_name: str
    owner: str
    description: Optional[str] = None
    stars: Optional[int] = None
    forks: Optional[int] = None
    open_issues: Optional[int] = None
    open_prs: Optional[int] = None
    
    
SYSTEM = """
You are a GitHub repository assistant with access to GitHub data through the GitHub CLI.

I can help you with:
- Listing and viewing pull requests
- Examining issues and their status
- Finding what issues are closed by pull requests
- Searching code within repositories
- Cloning repositories locally
- Examining commit history, especially commits before a PR was created

When answering questions about GitHub repositories, I'll use the GitHub CLI to get 
the most up-to-date information. If you want to work with a specific repository, 
I can clone it and then work with the files directly.

You can ask me to:
- List recent PRs or issues
- View details of specific PRs or issues
- Find what issues a PR closes
- Search for code patterns in repositories
- Clone repositories for deeper analysis
- Identify the commit before a PR branch was created

I'm best at answering specific questions that make use of GitHub's structure, 
for example finding connections between PRs and issues, or examining code across 
a repository.
"""


github_tools = [
    Tool(list_pull_requests),
    Tool(view_pull_request),
    Tool(list_issues),
    Tool(view_issue),
    Tool(get_pr_closing_issues),
    Tool(get_commit_before_pr),
    Tool(search_code),
    Tool(clone_repository),
    Tool(inspect_file),
    Tool(list_files),
]

github_agent = Agent(
    model="openai:gpt-4o",
    deps_type=GitHubDependencies,
    system_prompt=SYSTEM,
    tools=github_tools,
)