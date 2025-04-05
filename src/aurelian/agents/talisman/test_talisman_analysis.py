#!/usr/bin/env python3
"""
Test script for the Talisman agent's gene set analysis functionality.
This script tests the analysis of multiple genes to identify functional relationships.
"""

import sys
import os
from dataclasses import dataclass, field
from pydantic_ai import RunContext

from aurelian.agents.talisman.talisman_config import TalismanConfig, get_config
from aurelian.agents.talisman.talisman_tools import get_genes_from_list, analyze_gene_set

# Make sure we have an OpenAI API key
if "OPENAI_API_KEY" not in os.environ:
    print("Warning: OPENAI_API_KEY environment variable not set. Analysis may fail.")
    print("Set your API key with: export OPENAI_API_KEY=your_key_here")
    
# Custom context class that contains state property
@dataclass
class TestContext(RunContext):
    """Test context class that adds a state attribute."""
    state: object = field(default_factory=dict)

def test_talisman_gene_analysis(gene_list_str):
    """Test the Talisman agent's gene set analysis functionality.
    
    Args:
        gene_list_str: A string of gene IDs/symbols separated by commas
        
    Returns:
        The biological summary of the gene set
    """
    # Create a run context with config
    config = get_config()
    ctx = TestContext(deps=config, state={})
    
    print(f"Talisman Agent - Analyzing genes: {gene_list_str}")
    
    # First get gene descriptions
    print("Retrieving gene information...")
    try:
        gene_descriptions = get_genes_from_list(ctx, gene_list_str)
        print("Successfully retrieved gene information.")
        
        # Now analyze the gene set
        print("Analyzing gene set relationships...")
        analysis = analyze_gene_set(ctx, gene_list_str)
        print("\nTalisman Gene Set Analysis:\n")
        return analysis
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Default gene set for testing - TP53 and MDM2 (well-known interaction)
    default_gene_list = "TP53, MDM2"
    
    print("Talisman Agent Gene Analysis Test")
    print("=================================")
    
    gene_list = default_gene_list
    if len(sys.argv) > 1:
        gene_list = sys.argv[1]
    
    result = test_talisman_gene_analysis(gene_list)
    if result:
        print(result)