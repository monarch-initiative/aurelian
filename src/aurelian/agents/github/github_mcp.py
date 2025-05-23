"""
MCP wrapper for the GitHub agent.

This module provides a multi-component protocol wrapper for the GitHub agent,
allowing it to be used via the MCP protocol.
"""
from typing import Dict, List, Optional, Union, Any

from mcp.agent import Session
from mcp.telemetry import metadata_event
from pydantic_ai import RunContext

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
from aurelian.dependencies.workdir import WorkDir


class GitHubMCP:
    """MCP wrapper for the GitHub agent."""
    
    def __init__(self, workdir: WorkDir):
        """
        Initialize the GitHub MCP wrapper.
        
        Args:
            workdir: The working directory for the agent
        """
        self.deps = GitHubDependencies()
        self.deps.workdir = workdir
    
    def _create_context(self) -> RunContext[GitHubDependencies]:
        """Create a RunContext with the dependencies."""
        return RunContext[GitHubDependencies](
            deps=self.deps,
            model="openai:gpt-4o",
            usage=None,
            prompt=""
        )
    
    def list_pull_requests(
        self, 
        state: str = "open", 
        limit: int = 10, 
        label: Optional[str] = None,
        author: Optional[str] = None,
        base_branch: Optional[str] = None,
        repo: Optional[str] = None,
        session: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        List pull requests from GitHub.
        
        Args:
            state: Filter by state (open, closed, merged, all)
            limit: Maximum number of PRs to return
            label: Filter by label
            author: Filter by author
            base_branch: Filter by base branch
            repo: Repository to list PRs from (format: owner/repo), defaults to current repo
            session: Optional MCP session
            
        Returns:
            List of pull requests as dictionaries
        """
        if session:
            metadata_event(session, {"tool": "list_pull_requests"})
        
        ctx = self._create_context()
        return list_pull_requests(ctx, state, limit, label, author, base_branch, repo)
    
    def view_pull_request(
        self, 
        pr_number: Union[int, str], 
        repo: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific pull request.
        
        Args:
            pr_number: The pull request number
            repo: Repository the PR belongs to (format: owner/repo), defaults to current repo
            session: Optional MCP session
            
        Returns:
            Pull request details as a dictionary
        """
        if session:
            metadata_event(session, {"tool": "view_pull_request", "pr_number": pr_number})
        
        ctx = self._create_context()
        return view_pull_request(ctx, pr_number, repo)
    
    def list_issues(
        self, 
        state: str = "open", 
        limit: int = 10, 
        label: Optional[str] = None,
        author: Optional[str] = None,
        assignee: Optional[str] = None,
        repo: Optional[str] = None,
        session: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        List issues from GitHub.
        
        Args:
            state: Filter by state (open, closed, all)
            limit: Maximum number of issues to return
            label: Filter by label
            author: Filter by author
            assignee: Filter by assignee
            repo: Repository to list issues from (format: owner/repo), defaults to current repo
            session: Optional MCP session
            
        Returns:
            List of issues as dictionaries
        """
        if session:
            metadata_event(session, {"tool": "list_issues"})
        
        ctx = self._create_context()
        return list_issues(ctx, state, limit, label, author, assignee, repo)
    
    def view_issue(
        self, 
        issue_number: Union[int, str], 
        repo: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific issue.
        
        Args:
            issue_number: The issue number
            repo: Repository the issue belongs to (format: owner/repo), defaults to current repo
            session: Optional MCP session
            
        Returns:
            Issue details as a dictionary
        """
        if session:
            metadata_event(session, {"tool": "view_issue", "issue_number": issue_number})
        
        ctx = self._create_context()
        return view_issue(ctx, issue_number, repo)
    
    def get_pr_closing_issues(
        self, 
        pr_number: Union[int, str], 
        repo: Optional[str] = None,
        session: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the issues that will be closed by a specific pull request.
        
        Args:
            pr_number: The pull request number
            repo: Repository the PR belongs to (format: owner/repo), defaults to current repo
            session: Optional MCP session
            
        Returns:
            List of issues closed by the PR
        """
        if session:
            metadata_event(session, {"tool": "get_pr_closing_issues", "pr_number": pr_number})
        
        ctx = self._create_context()
        return get_pr_closing_issues(ctx, pr_number, repo)
    
    def get_commit_before_pr(
        self, 
        pr_number: Union[int, str], 
        repo: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Dict[str, str]:
        """
        Get the commit hash before a PR branch was created.
        This identifies the commit from which the PR branch was created.
        
        Args:
            pr_number: The pull request number
            repo: Repository the PR belongs to (format: owner/repo), defaults to current repo
            session: Optional MCP session
            
        Returns:
            Dictionary with commit hash and message
        """
        if session:
            metadata_event(session, {"tool": "get_commit_before_pr", "pr_number": pr_number})
        
        ctx = self._create_context()
        return get_commit_before_pr(ctx, pr_number, repo)
    
    def search_code(
        self, 
        query: str, 
        repo: Optional[str] = None,
        session: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for code in a repository.
        
        Args:
            query: The search query
            repo: Repository to search in (format: owner/repo), defaults to current repo
            session: Optional MCP session
            
        Returns:
            List of code matches as dictionaries
        """
        if session:
            metadata_event(session, {"tool": "search_code", "query": query})
        
        ctx = self._create_context()
        return search_code(ctx, query, repo)
    
    def clone_repository(
        self, 
        repo: str,
        directory: Optional[str] = None,
        branch: Optional[str] = None,
        depth: Optional[int] = None,
        session: Optional[Session] = None
    ) -> str:
        """
        Clone a GitHub repository to a local directory.
        
        Args:
            repo: Repository to clone (format: owner/repo)
            directory: Directory name to clone into (defaults to repo name)
            branch: Branch to clone (defaults to default branch)
            depth: Depth limit for clone (use for shallow clones)
            session: Optional MCP session
            
        Returns:
            Path to the cloned repository
        """
        if session:
            metadata_event(session, {"tool": "clone_repository", "repo": repo})
        
        ctx = self._create_context()
        return clone_repository(ctx, repo, directory, branch, depth)