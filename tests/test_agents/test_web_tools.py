"""
Tests for the web tools.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from aurelian.agents.web.web_tools import perplexity_query, ResultWithCitations


@pytest.fixture
def mock_agent():
    """Fixture to mock the pydantic_ai Agent."""
    with patch("aurelian.agents.web.web_tools.Agent") as mock_agent_class:
        mock_instance = MagicMock()
        mock_agent_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_openai_model():
    """Fixture to mock the OpenAIModel."""
    with patch("aurelian.agents.web.web_tools.OpenAIModel") as mock_model_class:
        mock_instance = MagicMock()
        mock_model_class.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_perplexity_query(mock_agent, mock_openai_model):
    """Test the perplexity_query function."""
    # Setup the mock to return a sample XML response
    mock_result = MagicMock()
    mock_result.data = """
    <answer>
    This is a test answer about a scientific topic.
    </answer>
    <citations>
      <citation>
        <citation_number>1</citation_number>
        <url>https://example.com/citation1</url>
        <timestamp>2023-01-01</timestamp>
      </citation>
      <citation>
        <citation_number>2</citation_number>
        <url>https://example.com/citation2</url>
        <timestamp>2023-01-02</timestamp>
      </citation>
    </citations>
    """
    mock_agent.run_sync.return_value = mock_result
    
    # Set environment variable for test
    with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test_key"}):
        # Call the function
        result = await perplexity_query("Test query about science")
        
        # Verify the result
        assert isinstance(result, ResultWithCitations)
        assert "test answer about a scientific topic" in result.content
        assert len(result.citations) == 2
        assert result.citations[0].citation_number == "1"
        assert result.citations[0].url == "https://example.com/citation1"
        assert result.citations[0].timestamp == "2023-01-01"
        assert result.citations[1].citation_number == "2"
        assert result.citations[1].url == "https://example.com/citation2"
        
        # Verify the mock was called with expected arguments
        mock_agent.run_sync.assert_called_once_with("Test query about science")


@pytest.mark.asyncio
async def test_perplexity_query_custom_model(mock_agent, mock_openai_model):
    """Test the perplexity_query function with a custom model."""
    # Setup the mock
    mock_result = MagicMock()
    mock_result.data = """
    <answer>Custom model response</answer>
    <citations>
      <citation>
        <citation_number>1</citation_number>
        <url>https://example.com/citation1</url>
      </citation>
    </citations>
    """
    mock_agent.run_sync.return_value = mock_result
    
    # Set environment variable for test
    with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test_key"}):
        # Call the function with custom model
        result = await perplexity_query("Test query", model_name="sonar-pro")
        
        # Verify the result
        assert "Custom model response" in result.content
        assert len(result.citations) == 1
        
        # Verify the OpenAIModel was initialized with the correct model name
        mock_openai_model.assert_called_once()
        args, kwargs = mock_openai_model.call_args
        assert kwargs["model_name"] == "sonar-pro"


@pytest.mark.asyncio
async def test_perplexity_query_missing_api_key():
    """Test the perplexity_query function with a missing API key."""
    # Set environment variable for test
    with patch.dict(os.environ, {}, clear=True):
        # Call the function and expect an exception
        with pytest.raises(ValueError) as excinfo:
            await perplexity_query("Test query")
        
        # Verify the exception message
        assert "PERPLEXITY_API_KEY environment variable is not set" in str(excinfo.value)


@pytest.mark.asyncio
async def test_perplexity_query_empty_response(mock_agent, mock_openai_model):
    """Test the perplexity_query function with an empty response."""
    # Setup the mock to return an empty response
    mock_result = MagicMock()
    mock_result.data = """
    <answer></answer>
    <citations></citations>
    """
    mock_agent.run_sync.return_value = mock_result
    
    # Set environment variable for test
    with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test_key"}):
        # Call the function
        result = await perplexity_query("Test query")
        
        # Verify the result
        assert result.content == ""
        assert len(result.citations) == 0


@pytest.mark.asyncio
async def test_perplexity_query_parsing_error(mock_agent, mock_openai_model):
    """Test the perplexity_query function with a response that causes a parsing error."""
    # Setup the mock to return a malformed response
    mock_result = MagicMock()
    mock_result.data = "<malformed>XML that will cause parsing error"
    mock_agent.run_sync.return_value = mock_result
    
    # Set environment variable for test
    with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test_key"}):
        # Call the function and expect an exception
        with pytest.raises(RuntimeError) as excinfo:
            await perplexity_query("Test query")
        
        # Verify the exception message
        assert "Failed to parse Perplexity response" in str(excinfo.value)


# Integration tests (when not in CI environment)
if os.getenv("GITHUB_ACTIONS") != "true" and os.getenv("PERPLEXITY_API_KEY"):
    pytestmark = [
        pytest.mark.integration,
        pytest.mark.flaky(reruns=1, reruns_delay=2),
    ]
    
    @pytest.mark.asyncio
    async def test_perplexity_query_integration():
        """Integration test for the perplexity_query function with real API calls."""
        # Skip test if API key is not available
        if not os.getenv("PERPLEXITY_API_KEY"):
            pytest.skip("PERPLEXITY_API_KEY environment variable is not set")
        
        # Call the function
        result = await perplexity_query("What is the capital of France?")
        
        # Verify the result
        assert result.content is not None
        assert "Paris" in result.content
        assert isinstance(result.citations, list)