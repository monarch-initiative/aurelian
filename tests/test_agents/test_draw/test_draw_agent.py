"""
Tests for the Draw Agent.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from aurelian.agents.draw.draw_config import DrawDependencies
from aurelian.agents.draw.draw_agent import draw_agent
from aurelian.agents.draw.draw_tools import (
    create_svg_drawing,
    convert_svg_to_png,
    svg_to_data_url,
    judge_drawing
)
from pydantic_ai import RunContext, ModelRetry


def test_create_svg_drawing():
    """Test that create_svg_drawing raises ModelRetry."""
    ctx = RunContext[DrawDependencies](
        deps=DrawDependencies(),
        model=None, usage=None, prompt=None,
    )
    
    with pytest.raises(ModelRetry):
        # This should raise a ModelRetry as it's supposed to be handled by the LLM
        create_svg_drawing(ctx, "A simple cat face")


def test_convert_svg_to_png():
    """Test convert_svg_to_png size limit."""
    ctx = RunContext[DrawDependencies](
        deps=DrawDependencies(max_svg_size=10),  # Small size for testing
        model=None, usage=None, prompt=None,
    )
    
    # Test size limit
    with pytest.raises(ValueError, match="exceeds maximum size"):
        convert_svg_to_png(ctx, "<svg>Large SVG content that exceeds limit</svg>")


def test_svg_to_data_url():
    """Test svg_to_data_url functionality."""
    ctx = RunContext[DrawDependencies](
        deps=DrawDependencies(),
        model=None, usage=None, prompt=None,
    )
    
    # Test with simple SVG
    svg = "<svg width='100' height='100'><circle cx='50' cy='50' r='40' fill='red'/></svg>"
    data_url = svg_to_data_url(ctx, svg)
    
    assert data_url.startswith("data:image/svg+xml;base64,")
    assert len(data_url) > 30  # Should have a reasonable length


@patch('aurelian.agents.draw.draw_tools.convert_svg_to_png')
@patch('aurelian.agents.draw.draw_tools.drawing_judge_agent')
def test_judge_drawing(mock_judge_agent, mock_convert):
    """Test judge_drawing functionality."""
    # Set up mocks
    mock_convert.return_value = b"PNG_BYTES"
    mock_result = MagicMock()
    mock_result.data = "This is good feedback"
    mock_judge_agent.run.return_value = mock_result
    
    ctx = RunContext[DrawDependencies](
        deps=DrawDependencies(),
        model=None, usage=None, prompt=None,
    )
    
    # Test judge feedback
    result = judge_drawing(ctx, "<svg>test</svg>", "A cat")
    
    assert result == "This is good feedback"
    mock_convert.assert_called_once()
    mock_judge_agent.run.assert_called_once()