"""Integration tests for GitHub agent tools.

These tests are skipped by default unless specific environment variables are set.
"""
import os
import pytest
import tempfile
import shutil

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
    search_code,
    clone_repository
)

# Skip on CI or if no GitHub credentials available
skip_integration = pytest.mark.skipif(
    os.getenv("AURELIAN_RUN_GITHUB_INTEGRATION_TESTS") != "true",
    reason="Skipping GitHub integration tests. Set AURELIAN_RUN_GITHUB_INTEGRATION_TESTS=true to run."
)

@pytest.fixture
def test_workdir():
    """Real workdir fixture for integration tests."""
    return WorkDir(location=os.getcwd())

@pytest.fixture
def test_context(test_workdir):
    """Real context with workdir fixture for integration tests."""
    deps = HasWorkdir()
    deps.workdir = test_workdir
    return MockContext(deps)

# Note: All of these tests use a known public repository to avoid authentication issues

@skip_integration
def test_list_pull_requests_integration(test_context):
    """Test actual API call to GitHub to list PRs."""
    # Use a known public repository with some PRs
    result = list_pull_requests(test_context, repo="monarch-initiative/aurelian", limit=5)
    
    # Basic validation
    assert isinstance(result, list)
    if result:
        assert "number" in result[0]
        assert "title" in result[0]
        assert "author" in result[0]
        assert "baseRefName" in result[0]

@skip_integration
def test_view_pull_request_integration(test_context):
    """Test actual API call to GitHub to view a specific PR."""
    # Assuming PR #31 exists in the repository
    result = view_pull_request(test_context, 31, repo="monarch-initiative/aurelian")
    
    # Basic validation
    assert isinstance(result, dict)
    assert "number" in result
    assert result["number"] == 31
    assert "title" in result
    assert "author" in result

@skip_integration
def test_list_issues_integration(test_context):
    """Test actual API call to GitHub to list issues."""
    result = list_issues(test_context, repo="monarch-initiative/aurelian", limit=5)
    
    # Basic validation
    assert isinstance(result, list)
    if result:
        assert "number" in result[0]
        assert "title" in result[0]
        assert "author" in result[0]

@skip_integration
def test_view_issue_integration(test_context):
    """Test actual API call to GitHub to view a specific issue."""
    # Use first issue from list or a known issue number
    issues = list_issues(test_context, repo="monarch-initiative/aurelian", limit=1)
    if issues:
        issue_number = issues[0]["number"]
        result = view_issue(test_context, issue_number, repo="monarch-initiative/aurelian")
        
        # Basic validation
        assert isinstance(result, dict)
        assert "number" in result
        assert result["number"] == issue_number
        assert "title" in result
        assert "author" in result

@skip_integration
def test_search_code_integration(test_context):
    """Test actual API call to GitHub to search code."""
    # Search for a term likely to be found in the repo
    result = search_code(test_context, "RunContext", repo="monarch-initiative/aurelian")
    
    # Basic validation
    assert isinstance(result, list)
    # There may be no results depending on the repo and search term
    if result:
        assert "path" in result[0]
        assert "repository" in result[0]
        assert "textMatches" in result[0]

@skip_integration
def test_clone_repository_integration(test_context):
    """Test actual cloning of a GitHub repository."""
    # Create a temporary directory for this test
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a workdir object for the temp directory
        temp_workdir = WorkDir(location=temp_dir)
        
        # Create a context with the temp workdir
        deps = HasWorkdir()
        deps.workdir = temp_workdir
        temp_context = MockContext(deps)
        
        # Clone the cell-ontology repository (with depth=1 for speed)
        repo_path = clone_repository(
            temp_context, 
            "obophenotype/cell-ontology", 
            depth=1
        )
        
        # Verify the repository was cloned successfully
        assert os.path.exists(repo_path)
        assert os.path.isdir(repo_path)
        
        # Check for key files that should exist in the repository
        assert os.path.exists(os.path.join(repo_path, "README.md"))
        assert os.path.exists(os.path.join(repo_path, ".git"))
        
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)