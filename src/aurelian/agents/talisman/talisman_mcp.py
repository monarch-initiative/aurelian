"""
MCP tools for retrieving gene information using the UniProt API and NCBI Entrez.
"""
import os

from mcp.server.fastmcp import FastMCP

from aurelian.agents.talisman.talisman_agent import TALISMAN_SYSTEM_PROMPT
from aurelian.agents.talisman.talisman_config import TalismanConfig, get_config
from aurelian.agents.talisman.talisman_tools import (
    get_gene_description,
    get_gene_descriptions,
    get_genes_from_list,
    analyze_gene_set
)

from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("talisman", instructions=TALISMAN_SYSTEM_PROMPT)

def deps() -> TalismanConfig:
    """Get the Talisman dependencies."""
    return get_config()

def ctx() -> RunContext[TalismanConfig]:
    """Get the run context with dependencies."""
    rc: RunContext[TalismanConfig] = RunContext[TalismanConfig](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc

@mcp.tool()
async def get_gene_info(gene_id: str) -> str:
    """
    Get description for a single gene ID.
    
    Args:
        gene_id: The gene identifier (UniProt ID, gene symbol, etc.)
        
    Returns:
        The gene description in a structured format
    """
    return get_gene_description(ctx(), gene_id)

@mcp.tool()
async def get_multiple_gene_info(gene_ids: str) -> str:
    """
    Get descriptions for multiple gene IDs provided as a string.
    
    Args:
        gene_ids: String containing gene identifiers separated by commas, spaces, or newlines
        
    Returns:
        The gene descriptions in a structured format
    """
    return get_genes_from_list(ctx(), gene_ids)

@mcp.tool()
async def analyze_genes(gene_list: str) -> str:
    """
    Analyze a set of genes and generate a biological summary of their properties and relationships.
    
    Args:
        gene_list: String containing gene identifiers separated by commas, spaces, or newlines
        
    Returns:
        A structured biological summary of the gene set with Narrative, Functional Terms Table, and Gene Summary Table
    """
    return analyze_gene_set(ctx(), gene_list)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')