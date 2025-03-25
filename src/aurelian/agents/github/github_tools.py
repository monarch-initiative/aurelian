"""
Tools for interacting with GitHub via command line tools (gh and git).
"""
import json
import subprocess
import os
import asyncio
from typing import Dict, List, Optional, Union, Any, Protocol

from pydantic_ai import RunContext

from aurelian.dependencies.workdir import HasWorkdir

# Field constants for GitHub API responses
NUMBER = "number"
TITLE = "title"
AUTHOR = "author"
URL = "url"
STATE = "state"
CREATED_AT = "createdAt"
CLOSED_AT = "closedAt"
BODY = "body"
LABELS = "labels"
ASSIGNEES = "assignees"
COMMENTS = "comments"
BASE_REF_NAME = "baseRefName"
HEAD_REF_NAME = "headRefName"
IS_DRAFT = "isDraft"
COMMITS = "commits"
FILES = "files" 
REVIEWS = "reviews"
CLOSING_ISSUES = "closingIssues"
PATH = "path"
REPOSITORY = "repository"
TEXT_MATCHES = "textMatches"

# Field groupings for common use cases
CORE_FIELDS = [NUMBER, TITLE, AUTHOR, URL, STATE, CREATED_AT, CLOSED_AT, BODY]
ISSUE_FIELDS = CORE_FIELDS + [LABELS, ASSIGNEES]
ISSUE_DETAIL_FIELDS = ISSUE_FIELDS + [COMMENTS]
PR_FIELDS = CORE_FIELDS + [BASE_REF_NAME, HEAD_REF_NAME, IS_DRAFT, LABELS]
PR_DETAIL_FIELDS = PR_FIELDS + [COMMITS, FILES, COMMENTS, REVIEWS]
SEARCH_CODE_FIELDS = [PATH, REPOSITORY, TEXT_MATCHES]

async def _run_gh_command(args: List[str], cwd: Optional[str] = None) -> str:
    """
    Run a GitHub CLI command and return the output.
    
    Args:
        args: List of command line arguments to pass to gh
        cwd: Current working directory in which to run the command
        
    Returns:
        The command output as a string
        
    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    cmd = ["gh"] + args
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd
    )
    stdout, stderr = await proc.communicate()
    
    if proc.returncode != 0:
        error_msg = stderr.decode('utf-8').strip()
        raise subprocess.CalledProcessError(proc.returncode, cmd, stdout + stderr, stderr)
        
    return stdout.decode('utf-8').strip()

async def list_pull_requests(
    ctx: RunContext[HasWorkdir],
    state: str = "open", 
    limit: int = 10, 
    label: Optional[str] = None,
    author: Optional[str] = None,
    base_branch: Optional[str] = None,
    repo: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List pull requests from GitHub.
    
    Args:
        ctx: Run context with workdir dependency
        state: Filter by state (open, closed, merged, all)
        limit: Maximum number of PRs to return
        label: Filter by label
        author: Filter by author
        base_branch: Filter by base branch
        repo: Repository to list PRs from (format: owner/repo), defaults to current repo
        
    Returns:
        List of pull requests as dictionaries
    """
    # Get workdir location - handle both string and object workdirs
    workdir = ctx.deps.workdir
    if hasattr(workdir, 'location'):
        workdir = workdir.location
    
    args = ["pr", "list", "--json", ",".join(PR_FIELDS)]
    
    if state and state != "all":
        args.extend(["--state", state])
    
    if limit:
        args.extend(["--limit", str(limit)])
        
    if label:
        args.extend(["--label", label])
        
    if author:
        args.extend(["--author", author])
        
    if base_branch:
        args.extend(["--base", base_branch])
    
    if repo:
        args.extend(["--repo", repo])
    
    output = await _run_gh_command(args, cwd=workdir)
    return json.loads(output)

async def view_pull_request(
    ctx: RunContext[HasWorkdir],
    pr_number: Union[int, str], 
    repo: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific pull request.
    
    Args:
        ctx: Run context with workdir dependency
        pr_number: The pull request number
        repo: Repository the PR belongs to (format: owner/repo), defaults to current repo
        
    Returns:
        Pull request details as a dictionary
    """
    # Get workdir location - handle both string and object workdirs
    workdir = ctx.deps.workdir
    if hasattr(workdir, 'location'):
        workdir = workdir.location
        
    args = ["pr", "view", str(pr_number), "--json", ",".join(PR_DETAIL_FIELDS)]
    
    if repo:
        args.extend(["--repo", repo])
    
    output = await _run_gh_command(args, cwd=workdir)
    return json.loads(output)

async def list_issues(
    ctx: RunContext[HasWorkdir],
    state: str = "open", 
    limit: int = 10, 
    label: Optional[str] = None,
    author: Optional[str] = None,
    assignee: Optional[str] = None,
    repo: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List issues from GitHub.
    
    Args:
        ctx: Run context with workdir dependency
        state: Filter by state (open, closed, all)
        limit: Maximum number of issues to return
        label: Filter by label
        author: Filter by author
        assignee: Filter by assignee
        repo: Repository to list issues from (format: owner/repo), defaults to current repo
        
    Returns:
        List of issues as dictionaries
    """
    # Get workdir location - handle both string and object workdirs
    workdir = ctx.deps.workdir
    if hasattr(workdir, 'location'):
        workdir = workdir.location
        
    args = ["issue", "list", "--json", ",".join(ISSUE_FIELDS)]
    
    if state and state != "all":
        args.extend(["--state", state])
    
    if limit:
        args.extend(["--limit", str(limit)])
        
    if label:
        args.extend(["--label", label])
        
    if author:
        args.extend(["--author", author])
        
    if assignee:
        args.extend(["--assignee", assignee])
    
    if repo:
        args.extend(["--repo", repo])
    
    output = await _run_gh_command(args, cwd=workdir)
    return json.loads(output)

async def view_issue(
    ctx: RunContext[HasWorkdir],
    issue_number: Union[int, str], 
    repo: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific issue.
    
    Args:
        ctx: Run context with workdir dependency
        issue_number: The issue number
        repo: Repository the issue belongs to (format: owner/repo), defaults to current repo
        
    Returns:
        Issue details as a dictionary
    """
    # Get workdir location - handle both string and object workdirs
    workdir = ctx.deps.workdir
    if hasattr(workdir, 'location'):
        workdir = workdir.location
        
    args = ["issue", "view", str(issue_number), "--json", ",".join(ISSUE_DETAIL_FIELDS),
            "--color", "never"]
    
    if repo:
        args.extend(["--repo", repo])
    
    output = await _run_gh_command(args, cwd=workdir)
    return json.loads(output)

async def get_pr_closing_issues(
    ctx: RunContext[HasWorkdir],
    pr_number: Union[int, str], 
    repo: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get the issues that will be closed by a specific pull request.
    
    Args:
        ctx: Run context with workdir dependency
        pr_number: The pull request number
        repo: Repository the PR belongs to (format: owner/repo), defaults to current repo
        
    Returns:
        List of issues closed by the PR
    """
    pr_details = await view_pull_request(ctx, pr_number, repo)
    return pr_details.get(CLOSING_ISSUES, [])

async def _run_git_command(args: List[str], cwd: Optional[str] = None) -> str:
    """
    Run a git command and return the output.
    
    Args:
        args: List of command line arguments to pass to git
        cwd: Current working directory in which to run the command
        
    Returns:
        The command output as a string
        
    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    cmd = ["git"] + args
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd
    )
    stdout, stderr = await proc.communicate()
    
    if proc.returncode != 0:
        error_msg = stderr.decode('utf-8').strip()
        raise subprocess.CalledProcessError(proc.returncode, cmd, stdout, stderr)
        
    return stdout.decode('utf-8').strip()

async def get_commit_before_pr(
    ctx: RunContext[HasWorkdir],
    pr_number: Union[int, str], 
    repo: Optional[str] = None
) -> Dict[str, str]:
    """
    Get the commit hash before a PR branch was created.
    This identifies the commit from which the PR branch was created.
    
    Args:
        ctx: Run context with workdir dependency
        pr_number: The pull request number
        repo: Repository the PR belongs to (format: owner/repo), defaults to current repo
        
    Returns:
        Dictionary with commit hash and message
    """
    # Get workdir location - handle both string and object workdirs
    workdir = ctx.deps.workdir
    if hasattr(workdir, 'location'):
        workdir = workdir.location
    
    # First get PR details to identify the base and head branches
    pr_details = await view_pull_request(ctx, pr_number, repo)
    base_branch = pr_details["baseRefName"]
    head_branch = pr_details["headRefName"]
    
    # Get the first commit on the PR branch
    first_pr_commit = await _run_git_command(
        ["log", base_branch + ".." + head_branch, "--reverse", "--format=%H", "--max-count=1"],
        cwd=workdir
    )
    
    # Get the parent commit of the first PR commit (the commit before the PR started)
    base_commit = await _run_git_command(["rev-parse", first_pr_commit + "^"], cwd=workdir)
    commit_message = await _run_git_command(["log", "-1", "--format=%B", base_commit], cwd=workdir)
    
    return {
        "hash": base_commit,
        "message": commit_message
    }

async def search_code(
    ctx: RunContext[HasWorkdir],
    query: str, 
    repo: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for code in a repository.
    
    Args:
        ctx: Run context with workdir dependency
        query: The search query
        repo: Repository to search in (format: owner/repo), defaults to current repo
        
    Returns:
        List of code matches as dictionaries
    """
    # Get workdir location - handle both string and object workdirs
    workdir = ctx.deps.workdir
    if hasattr(workdir, 'location'):
        workdir = workdir.location
        
    args = ["search", "code", query, "--json", ",".join(SEARCH_CODE_FIELDS)]
    
    if repo:
        query = f"repo:{repo} {query}"
        args[2] = query
    
    output = await _run_gh_command(args, cwd=workdir)
    return json.loads(output)

async def clone_repository(
    ctx: RunContext[HasWorkdir],
    repo: str,
    directory: Optional[str] = None,
    branch: Optional[str] = None,
    depth: Optional[int] = None
) -> str:
    """
    Clone a GitHub repository to a local directory.
    
    Args:
        ctx: Run context with workdir dependency
        repo: Repository to clone (format: owner/repo)
        directory: Directory name to clone into (defaults to repo name)
        branch: Branch to clone (defaults to default branch)
        depth: Depth limit for clone (use for shallow clones)
        
    Returns:
        Path to the cloned repository
    """
    # Get workdir location - handle both string and object workdirs
    workdir = ctx.deps.workdir
    if hasattr(workdir, 'location'):
        workdir = workdir.location
    
    # Build command
    args = ["repo", "clone", repo]
    
    # Add optional directory
    if directory:
        args.append(directory)
    else:
        # Default to repo name
        directory = repo.split("/")[-1]

    # check if directory exists
    if os.path.exists(os.path.join(workdir, directory)):
        raise FileExistsError(f"Directory {directory} already exists.")
    
    # Add branch if specified
    if branch:
        args.extend(["--branch", branch])
    
    # Add depth if specified
    if depth:
        args.extend(["--depth", str(depth)])
    
    # Run the clone command
    await _run_gh_command(args, cwd=workdir)
    
    # Return the full path to the cloned repo
    if os.path.isabs(workdir):
        return os.path.join(workdir, directory)
    else:
        # If workdir is relative, make it absolute
        abs_workdir = os.path.abspath(workdir)
        return os.path.join(abs_workdir, directory)