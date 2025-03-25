"""Tests for GitHub agent tools."""
import json
import os
import subprocess
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

class WorkDir:
    def __init__(self, location: str):
        self.location = location

class HasWorkdir:
    def __init__(self):
        self.workdir = None

class MockContext:
    def __init__(self, deps):
        self.deps = deps

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

@pytest.fixture
def mock_workdir():
    """Mock workdir fixture."""
    return WorkDir(location="/tmp/test_github")

@pytest.fixture
def mock_context(mock_workdir):
    """Mock context with workdir fixture."""
    deps = HasWorkdir()
    deps.workdir = mock_workdir
    return MockContext(deps)

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.asyncio.create_subprocess_exec')
async def test_list_pull_requests(mock_subprocess, mock_context):
    """Test listing pull requests."""
    # Setup mock response
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (
        json.dumps([{
            "number": 123,
            "title": "Test PR",
            "author": {"login": "testuser"},
            "url": "https://github.com/test/repo/pull/123",
            "state": "open",
            "createdAt": "2023-01-01T00:00:00Z",
            "closedAt": None,
            "body": "PR description",
            "baseRefName": "main",
            "headRefName": "feature-branch",
            "isDraft": False,
            "labels": []
        }]).encode('utf-8'),
        b''
    )
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process
    
    # Call function
    result = await list_pull_requests(mock_context)
    
    # Assertions
    assert len(result) == 1
    assert result[0]["number"] == 123
    assert result[0]["title"] == "Test PR"
    
    # Verify correct command was called
    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    assert args[0:3] == ("gh", "pr", "list")
    assert kwargs["cwd"] == "/tmp/test_github"

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.asyncio.create_subprocess_exec')
async def test_view_pull_request(mock_subprocess, mock_context):
    """Test viewing a specific pull request."""
    # Setup mock response
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (
        json.dumps({
            "number": 123,
            "title": "Test PR",
            "author": {"login": "testuser"},
            "url": "https://github.com/test/repo/pull/123",
            "state": "open",
            "createdAt": "2023-01-01T00:00:00Z",
            "closedAt": None,
            "body": "PR description",
            "baseRefName": "main",
            "headRefName": "feature-branch",
            "commits": [{"oid": "abc123"}],
            "files": [{"path": "README.md"}],
            "comments": [],
            "reviews": [],
            "closingIssues": [{"number": 456, "title": "Issue to close"}]
        }).encode('utf-8'),
        b''
    )
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process
    
    # Call function
    result = await view_pull_request(mock_context, 123)
    
    # Assertions
    assert result["number"] == 123
    assert result["title"] == "Test PR"
    assert len(result["closingIssues"]) == 1
    assert result["closingIssues"][0]["number"] == 456
    
    # Verify correct command was called
    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    assert args[0:4] == ("gh", "pr", "view", "123")
    assert kwargs["cwd"] == "/tmp/test_github"

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.asyncio.create_subprocess_exec')
async def test_list_issues(mock_subprocess, mock_context):
    """Test listing issues."""
    # Setup mock response
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (
        json.dumps([{
            "number": 456,
            "title": "Test Issue",
            "author": {"login": "testuser"},
            "url": "https://github.com/test/repo/issues/456",
            "state": "open",
            "createdAt": "2023-01-01T00:00:00Z",
            "closedAt": None,
            "body": "Issue description",
            "labels": [{"name": "bug"}],
            "assignees": []
        }]).encode('utf-8'),
        b''
    )
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process
    
    # Call function
    result = await list_issues(mock_context, label="bug")
    
    # Assertions
    assert len(result) == 1
    assert result[0]["number"] == 456
    assert result[0]["title"] == "Test Issue"
    assert result[0]["labels"][0]["name"] == "bug"
    
    # Verify correct command was called
    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    assert args[0:3] == ("gh", "issue", "list")
    assert "--label" in args
    assert "bug" in args
    assert kwargs["cwd"] == "/tmp/test_github"

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.view_pull_request')
async def test_get_pr_closing_issues(mock_view_pr, mock_context):
    """Test getting issues that will be closed by a PR."""
    # Setup mock response
    mock_view_pr.return_value = {
        "number": 123,
        "title": "Test PR",
        "closingIssues": [
            {"number": 456, "title": "Issue 1"},
            {"number": 789, "title": "Issue 2"}
        ]
    }
    
    # Call function
    result = await get_pr_closing_issues(mock_context, 123)
    
    # Assertions
    assert len(result) == 2
    assert result[0]["number"] == 456
    assert result[1]["number"] == 789
    
    # Verify view_pull_request was called with correct arguments
    mock_view_pr.assert_called_once_with(mock_context, 123, None)

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools._run_git_command')
@patch('aurelian.agents.github.github_tools.view_pull_request')
async def test_get_commit_before_pr(mock_view_pr, mock_git_command, mock_context):
    """Test getting the commit before a PR was created."""
    # Setup mock responses
    mock_view_pr.return_value = {
        "baseRefName": "main",
        "headRefName": "feature-branch"
    }
    
    # Mock sequence of _run_git_command calls
    mock_git_command.side_effect = [
        "abc123def456",  # First commit on PR branch
        "987654321",     # Parent commit hash
        "Commit message" # Commit message
    ]
    
    # Call function
    result = await get_commit_before_pr(mock_context, 123)
    
    # Assertions
    assert result["hash"] == "987654321"
    assert result["message"] == "Commit message"
    
    # Verify correct sequence of calls
    assert mock_git_command.call_count == 3
    call_args_list = mock_git_command.call_args_list
    assert "log" in call_args_list[0][0][0]
    assert "rev-parse" in call_args_list[1][0][0]
    assert "log" in call_args_list[2][0][0]

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.asyncio.create_subprocess_exec')
async def test_search_code(mock_subprocess, mock_context):
    """Test searching code in a repository."""
    # Setup mock response
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (
        json.dumps([{
            "path": "src/file.py",
            "repository": {"name": "testrepo"},
            "textMatches": [{"fragment": "def test_function():"}]
        }]).encode('utf-8'),
        b''
    )
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process
    
    # Call function
    result = await search_code(mock_context, "test_function")
    
    # Assertions
    assert len(result) == 1
    assert result[0]["path"] == "src/file.py"
    assert "test_function" in result[0]["textMatches"][0]["fragment"]
    
    # Verify correct command was called
    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    assert args[0:3] == ("gh", "search", "code")
    assert "test_function" in args
    assert kwargs["cwd"] == "/tmp/test_github"

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.asyncio.create_subprocess_exec')
async def test_list_pull_requests_with_all_options(mock_subprocess, mock_context):
    """Test listing pull requests with all option parameters."""
    # Setup mock response
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (
        json.dumps([]).encode('utf-8'),
        b''
    )
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process
    
    # Call function with all parameters
    await list_pull_requests(
        mock_context,
        state="closed", 
        limit=5, 
        label="enhancement", 
        author="octocat", 
        base_branch="main", 
        repo="owner/repo"
    )
    
    # Verify command construction
    args, kwargs = mock_subprocess.call_args
    
    assert "--state" in args
    assert "closed" in args
    assert "--limit" in args
    assert "5" in args
    assert "--label" in args
    assert "enhancement" in args
    assert "--author" in args
    assert "octocat" in args
    assert "--base" in args
    assert "main" in args
    assert "--repo" in args
    assert "owner/repo" in args

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.asyncio.create_subprocess_exec')
async def test_error_handling(mock_subprocess, mock_context):
    """Test error handling when subprocess raises an exception."""
    # Setup mock process with error
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b'', b'Command failed')
    mock_process.returncode = 1
    mock_subprocess.return_value = mock_process
    
    # Verify exception is propagated
    with pytest.raises(subprocess.CalledProcessError):
        await list_pull_requests(mock_context)

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.asyncio.create_subprocess_exec')
async def test_clone_repository(mock_subprocess, mock_context):
    """Test cloning a repository."""
    # Setup mock response
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b'', b'')
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process
    
    # Call function with default parameters
    result = await clone_repository(mock_context, "obophenotype/cell-ontology")
    
    # Verify correct command was called
    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    assert args[0:3] == ("gh", "repo", "clone")
    assert args[3] == "obophenotype/cell-ontology"
    assert kwargs["cwd"] == "/tmp/test_github"
    
    # Verify returned path
    assert result == "/tmp/test_github/cell-ontology"

@pytest.mark.asyncio
@patch('aurelian.agents.github.github_tools.asyncio.create_subprocess_exec')
async def test_clone_repository_with_options(mock_subprocess, mock_context):
    """Test cloning a repository with all options."""
    # Setup mock response
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b'', b'')
    mock_process.returncode = 0
    mock_subprocess.return_value = mock_process
    
    # Call function with all parameters
    result = await clone_repository(
        mock_context, 
        "obophenotype/cell-ontology", 
        directory="custom-dir",
        branch="develop",
        depth=1
    )
    
    # Verify correct command was called
    mock_subprocess.assert_called_once()
    args, kwargs = mock_subprocess.call_args
    
    assert "gh" == args[0]
    assert "repo" == args[1]
    assert "clone" == args[2]
    assert "obophenotype/cell-ontology" == args[3]
    assert "custom-dir" == args[4]
    assert "--branch" in args
    assert "develop" in args
    assert "--depth" in args
    assert "1" in args
    assert kwargs["cwd"] == "/tmp/test_github"
    
    # Verify returned path
    assert result == "/tmp/test_github/custom-dir"