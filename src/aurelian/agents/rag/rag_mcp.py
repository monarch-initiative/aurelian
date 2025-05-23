"""
MCP tools for retrieval-augmented generation (RAG) against document collections.
"""
import os
from typing import Dict, List

from mcp.server.fastmcp import FastMCP

import aurelian.agents.rag.rag_tools as rt
from aurelian.agents.rag.rag_agent import rag_agent
from aurelian.agents.rag.rag_config import RagDependencies
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("rag", instructions=rag_agent.system_prompt)


from aurelian.dependencies.workdir import WorkDir

def deps() -> RagDependencies:
    deps = RagDependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[RagDependencies]:
    rc: RunContext[RagDependencies] = RunContext[RagDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def search_documents(query: str) -> List[Dict]:
    """
    Performs a retrieval search over the RAG database.
    
    Args:
        query: The search query (any text, such as name of a disease, phenotype, gene, etc.)
        
    Returns:
        A list of document objects matching the query with relevancy scores
    """
    return await rt.search_documents(ctx(), query)


@mcp.tool()
async def inspect_document(query: str) -> str:
    """
    Returns the content of the document.
    
    Args:
        query: E.g. title
        
    Returns:
        The full content of the document
    """
    return await rt.inspect_document(ctx(), query)


@mcp.tool()
async def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.
    
    Args:
        pmid: The PubMed ID to look up (format: "PMID:nnnnnnn")
        
    Returns:
        The full text if available, otherwise abstract
    """
    return await rt.lookup_pmid(ctx(), pmid)


@mcp.tool()
async def search_web(query: str) -> str:
    """
    Search the web using a text query.
    
    Args:
        query: The search query
        
    Returns:
        Matching web pages plus summaries
    """
    return await rt.search_web(ctx(), query)


@mcp.tool()
async def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.
    
    Args:
        url: The URL to fetch
        
    Returns:
        The contents of the web page
    """
    return await rt.retrieve_web_page(ctx(), url)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')