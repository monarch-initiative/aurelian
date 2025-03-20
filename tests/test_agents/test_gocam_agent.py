import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from aurelian.agents.gocam.gocam_agent import gocam_agent


@pytest.fixture
def deps():
    return GOCAMDependencies()


@pytest.mark.parametrize(
    "query,ideal",
    [
        ("Find a model relating to apoptosis and list their genes", "CASP"),
        ("How many distinct gene products in 62b4ffe300001804? Answer with a number, e.g. 7.", "4"),
        ("Find a model with ID gomodel:1234 and summarize it", None),
        ("When curating GO-CAMs, the activity unit for a ligand of a signaling receptor should use which GO MF ID for the activity unit?",
         "0048018"),
    ],
)
def test_gocam_agent(deps, query, ideal):
    r = gocam_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    if ideal is not None:
        assert ideal in data


def test_gocam_document_fetch(deps):
    """Test that the agent can retrieve GO-CAM documentation."""
    query = "What are the best practices for annotating signaling receptor activity?"
    r = gocam_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    
    # Check if the response contains key concepts from the signaling document
    # These should be present if it properly fetched the document
    expected_terms = ["receptor", "signaling", "activity"]
    for term in expected_terms:
        assert term.lower() in data.lower()
    
    # Test direct document fetching
    query = "Please fetch and summarize the document about signaling receptor activity annotation guidelines"
    r = gocam_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    assert "receptor" in data.lower()
    assert "signaling" in data.lower()


def test_gocam_model_validation(deps):
    """Test that the agent can validate GO-CAM models."""
    # Valid minimal model
    valid_model = {
        "id": "gomodel:test123",
        "title": "Test Model"
    }
    
    # Invalid model missing required field
    invalid_model = {
        "title": "Invalid Test Model"
    }
    
    # Test with valid model
    query = f"Please validate this GO-CAM model: {valid_model}"
    r = gocam_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    assert "valid" in data.lower()
    
    # Test with invalid model
    query = f"Please validate this GO-CAM model: {invalid_model}"
    r = gocam_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    assert "invalid" in data.lower() or "error" in data.lower()
