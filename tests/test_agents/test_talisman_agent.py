# test_talisman_agent.py

"""
Tests for the talisman agent.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from aurelian.agents.talisman.talisman_agent import talisman_agent
from aurelian.agents.talisman.talisman_tools import get_gene_description, get_gene_descriptions, get_genes_from_list, analyze_gene_set


@pytest.mark.skipif("OPENAI_API_KEY" not in os.environ, reason="Requires OpenAI API key")
def test_get_gene_description():
    """Test the get_gene_description function."""
    # This is a simple test to ensure the function doesn't raise an exception
    # We're not testing the actual content because it depends on external APIs
    with patch('aurelian.agents.talisman.talisman_tools.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.get_uniprot_client.return_value = MagicMock()
        mock_config.get_ncbi_client.return_value = MagicMock()
        mock_get_config.return_value = mock_config
        
        # Mock the RunContext
        mock_ctx = MagicMock()
        mock_ctx.deps = mock_config
        
        # Mock uniprot client search method
        mock_uniprot = MagicMock()
        mock_uniprot.search.return_value = "Entry\tGene names\nP53_HUMAN\tTP53"
        mock_uniprot.retrieve.return_value = "Mock UniProt entry data"
        mock_config.get_uniprot_client.return_value = mock_uniprot
        
        # Mock the NCBI client
        mock_ncbi = MagicMock()
        mock_config.get_ncbi_client.return_value = mock_ncbi
        
        # Test with a gene symbol
        result = get_gene_description(mock_ctx, "TP53")
        assert result is not None
        assert isinstance(result, str)


@pytest.mark.skipif("OPENAI_API_KEY" not in os.environ, reason="Requires OpenAI API key")
def test_get_gene_descriptions():
    """Test the get_gene_descriptions function."""
    with patch('aurelian.agents.talisman.talisman_tools.get_gene_description') as mock_get_gene_description:
        mock_get_gene_description.return_value = "Mock gene description"
        
        # Mock the RunContext
        mock_ctx = MagicMock()
        mock_ctx.deps = MagicMock()
        
        # Test with a list of gene symbols
        result = get_gene_descriptions(mock_ctx, ["TP53", "BRCA1"])
        assert result is not None
        assert isinstance(result, str)
        assert mock_get_gene_description.call_count == 2


@pytest.mark.skipif("OPENAI_API_KEY" not in os.environ, reason="Requires OpenAI API key")
def test_get_genes_from_list():
    """Test the get_genes_from_list function."""
    with patch('aurelian.agents.talisman.talisman_tools.get_gene_descriptions') as mock_get_gene_descriptions:
        mock_get_gene_descriptions.return_value = "Mock gene descriptions"
        
        # Mock the RunContext
        mock_ctx = MagicMock()
        mock_ctx.deps = MagicMock()
        
        # Test with a comma-separated list of gene symbols
        result = get_genes_from_list(mock_ctx, "TP53, BRCA1")
        assert result is not None
        assert isinstance(result, str)
        mock_get_gene_descriptions.assert_called_once()


@pytest.mark.skipif("OPENAI_API_KEY" not in os.environ, reason="Requires OpenAI API key")
def test_analyze_gene_set():
    """Test the analyze_gene_set function."""
    with patch('aurelian.agents.talisman.talisman_tools.get_genes_from_list') as mock_get_genes_from_list, \
         patch('aurelian.agents.talisman.talisman_tools.get_gene_description') as mock_get_gene_description, \
         patch('aurelian.agents.talisman.talisman_tools.openai.chat.completions.create') as mock_openai_create:
        
        mock_get_genes_from_list.return_value = "Mock gene descriptions"
        mock_get_gene_description.return_value = "Mock gene description"
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mock analysis result"
        mock_openai_create.return_value = mock_response
        
        # Mock the RunContext
        mock_ctx = MagicMock()
        mock_ctx.deps = MagicMock()
        mock_ctx.gene_info_dict = {"TP53": "Mock gene info", "BRCA1": "Mock gene info"}
        
        # Test with a comma-separated list of gene symbols
        result = analyze_gene_set(mock_ctx, "TP53, BRCA1")
        assert result is not None
        assert isinstance(result, str)
        mock_get_genes_from_list.assert_called_once()
        mock_openai_create.assert_called_once()