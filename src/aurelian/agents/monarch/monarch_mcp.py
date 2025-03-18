"""
MCP tools for interacting with the Monarch Knowledge Base.
"""
import os
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP

import aurelian.agents.monarch.monarch_tools as mt
from aurelian.agents.monarch.monarch_agent import MONARCH_SYSTEM_PROMPT
from aurelian.agents.monarch.monarch_config import MonarchDependencies, get_config
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("monarch", instructions=MONARCH_SYSTEM_PROMPT)


from aurelian.dependencies.workdir import WorkDir

def deps() -> MonarchDependencies:
    deps = get_config()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[MonarchDependencies]:
    rc: RunContext[MonarchDependencies] = RunContext[MonarchDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def find_gene_associations(gene_id: str) -> List[Dict]:
    """
    Find associations for a given gene or gene product.

    Args:
        gene_id: Gene identifier (e.g., HGNC symbol like "BRCA1")
        
    Returns:
        List of association objects containing subject, predicate, object details
    """
    return await mt.find_gene_associations(ctx(), gene_id)


@mcp.tool()
async def find_disease_associations(disease_id: str) -> List[Dict]:
    """
    Find associations for a given disease.

    Args:
        disease_id: Disease identifier (e.g., MONDO:0007254)
        
    Returns:
        List of association objects containing subject, predicate, object details
    """
    return await mt.find_disease_associations(ctx(), disease_id)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')