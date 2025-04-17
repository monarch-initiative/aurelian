#!/usr/bin/env python3
"""
Test script for the Talisman agent's gene set analysis functionality.
This script tests the analysis of multiple genes to identify functional relationships.
"""

import os
import sys
import pytest
from dataclasses import dataclass, field
from pydantic_ai import RunContext
from unittest.mock import patch, MagicMock

from aurelian.agents.talisman.talisman_config import TalismanConfig, get_config
from aurelian.agents.talisman.talisman_tools import get_genes_from_list, analyze_gene_set

# Custom context class that contains state property
@dataclass
class TestContext(RunContext):
    """Test context class that adds a state attribute."""
    state: object = field(default_factory=dict)


@pytest.mark.skipif("OPENAI_API_KEY" not in os.environ, reason="Requires OpenAI API key")
def test_talisman_gene_analysis():
    """Test the Talisman agent's gene set analysis functionality."""
    # Create a run context with config
    config = get_config()
    ctx = TestContext(deps=config, state={})
    
    gene_list_str = "TP53, MDM2"
    
    # Mock the necessary functions to avoid actual API calls
    with patch('aurelian.agents.talisman.talisman_tools.get_genes_from_list') as mock_get_genes_from_list, \
         patch('aurelian.agents.talisman.talisman_tools.get_gene_description') as mock_get_gene_description, \
         patch('aurelian.agents.talisman.talisman_tools.openai.chat.completions.create') as mock_openai_create:
        
        # Set up mock returns
        mock_get_genes_from_list.return_value = "Mock gene descriptions"
        mock_get_gene_description.return_value = "Mock gene description"
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        
        # Create a mock analysis with proper format including Terms and Gene Summary Table
        mock_analysis = """
# Gene Set Analysis
This is a mock analysis of TP53 and MDM2 genes.

## Functional Relationships
TP53 and MDM2 are involved in cell cycle regulation.

## Terms
DNA damage response; p53 signaling pathway; apoptosis; cell cycle regulation

## Gene Summary Table
| ID | Annotation | Genomic Context | Organism | Description |
|-------------|-------------|----------|----------------|------------|
| TP53 | NC_000017.11 (7668402..7687550) | Chromosome 17 | Homo sapiens | Tumor suppressor protein |
| MDM2 | NC_000012.12 (68808172..68850686) | Chromosome 12 | Homo sapiens | E3 ubiquitin-protein ligase |
"""
        mock_response.choices[0].message.content = mock_analysis
        mock_openai_create.return_value = mock_response
        
        # Set up gene_info_dict in context
        ctx.gene_info_dict = {
            "TP53": "Mock TP53 info",
            "MDM2": "Mock MDM2 info"
        }
        
        # Test the gene analysis
        analysis = analyze_gene_set(ctx, gene_list_str)
        
        # Verify result
        assert analysis is not None
        assert "## Terms" in analysis
        assert "## Gene Summary Table" in analysis
        assert "| ID | Annotation | Genomic Context | Organism | Description |" in analysis