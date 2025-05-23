"""
MCP tools for creating ontology mappings.
"""
import os
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP

import aurelian.agents.ontology_mapper.ontology_mapper_tools as omt
from aurelian.agents.ontology_mapper.ontology_mapper_agent import ONTOLOGY_MAPPER_SYSTEM_PROMPT
from aurelian.agents.ontology_mapper.ontology_mapper_config import OntologyMapperDependencies, get_config
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("ontology_mapper", instructions=ONTOLOGY_MAPPER_SYSTEM_PROMPT)


from aurelian.dependencies.workdir import WorkDir

def deps() -> OntologyMapperDependencies:
    deps = get_config()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[OntologyMapperDependencies]:
    rc: RunContext[OntologyMapperDependencies] = RunContext[OntologyMapperDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def search_terms(query: str, ont: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """
    Search for ontology terms matching a query.

    Args:
        query: The search query text
        ont: Optional ontology ID to search in (e.g., 'cl', 'go', 'uberon')
        limit: Maximum number of results to return
        
    Returns:
        List of matching ontology terms with their details
    """
    return await omt.search_terms(ctx(), query, ont, limit)


@mcp.tool()
async def search_web(query: str) -> str:
    """
    Search the web for ontology-related information.

    Args:
        query: The search query
        
    Returns:
        Search results with summaries
    """
    return await omt.search_web(ctx(), query)


@mcp.tool()
async def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page related to ontologies.

    Args:
        url: The URL to fetch
        
    Returns:
        The contents of the web page
    """
    return await omt.retrieve_web_page(ctx(), url)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')