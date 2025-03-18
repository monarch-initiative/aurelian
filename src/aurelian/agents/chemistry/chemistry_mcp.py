"""
MCP tools for working with chemical structures.
"""
import os
from typing import Dict, List

from mcp.server.fastmcp import FastMCP

import aurelian.agents.chemistry.chemistry_tools as ct
import aurelian.agents.filesystem.filesystem_tools as fst
from aurelian.agents.chemistry.chemistry_agent import SYSTEM
from aurelian.agents.chemistry.chemistry_config import ChemistryDependencies
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("chemistry", instructions=SYSTEM)


from aurelian.dependencies.workdir import WorkDir

def deps() -> ChemistryDependencies:
    deps = ChemistryDependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[ChemistryDependencies]:
    rc: RunContext[ChemistryDependencies] = RunContext[ChemistryDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def draw_structure_and_interpret(identifier: str, question: str) -> str:
    """
    Draw a chemical structure and analyze it.

    Args:
        identifier: A ChEBI ID (e.g., CHEBI:16236) or SMILES string
        question: A specific question about the structure
        
    Returns:
        Analysis of the structure in response to the question
    """
    return await ct.draw_structure_and_interpret(ctx(), identifier, question)


@mcp.tool()
async def chebi_search_terms(query: str) -> List[Dict]:
    """
    Search ChEBI for a term.

    Args:
        query: The search text
        
    Returns:
        A list of matching ChEBI terms
    """
    return await ct.chebi_search_terms(ctx(), query)


@mcp.tool()
async def search_web_for_chemistry(query: str) -> str:
    """
    Search the web for chemistry information.

    Args:
        query: The search query
        
    Returns:
        Search results with summaries
    """
    return await ct.search_web_for_chemistry(ctx(), query)


@mcp.tool()
async def retrieve_chemistry_web_page(url: str) -> str:
    """
    Fetch the contents of a web page related to chemistry.

    Args:
        url: The URL to fetch
        
    Returns:
        The contents of the web page
    """
    return await ct.retrieve_chemistry_web_page(ctx(), url)


@mcp.tool()
async def inspect_file(data_file: str) -> str:
    """
    Inspect a file in the working directory.

    Args:
        data_file: name of file
        
    Returns:
        Contents of the file
    """
    return await fst.inspect_file(ctx(), data_file)


@mcp.tool()
async def list_files() -> str:
    """
    List files in the working directory.

    Returns:
        List of files in the working directory
    """
    return await fst.list_files(ctx())


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')