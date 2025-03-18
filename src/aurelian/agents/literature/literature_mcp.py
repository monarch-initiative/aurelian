"""
MCP tools for working with scientific literature and publications.
"""
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

import aurelian.agents.literature.literature_tools as lt
import aurelian.agents.filesystem.filesystem_tools as fst
from aurelian.agents.literature.literature_agent import SYSTEM
from aurelian.agents.literature.literature_config import LiteratureDependencies
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("literature", instructions=SYSTEM)


from aurelian.dependencies.workdir import WorkDir

def deps() -> LiteratureDependencies:
    deps = LiteratureDependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[LiteratureDependencies]:
    rc: RunContext[LiteratureDependencies] = RunContext[LiteratureDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed article by its PMID.
    
    Args:
        pmid: The PubMed ID to look up (format: "PMID:nnnnnnn")
        
    Returns:
        Full text if available, otherwise abstract
    """
    return await lt.lookup_pmid(ctx(), pmid)

@mcp.tool()
async def lookup_doi(doi: str) -> str:
    """
    Lookup the text of an article by its DOI.
    
    Args:
        doi: The DOI to look up
        
    Returns:
        Full text if available, otherwise abstract
    """
    return await lt.lookup_doi(doi)


@mcp.tool()
async def convert_pmid_to_doi(pmid: str) -> str:
    """
    Convert a PubMed ID (PMID) to a DOI.
    
    Args:
        pmid: The PubMed ID to convert
        
    Returns:
        The corresponding DOI
    """
    return await lt.convert_pmid_to_doi(pmid)


@mcp.tool()
async def convert_doi_to_pmid(doi: str) -> str:
    """
    Convert a DOI to a PubMed ID (PMID).
    
    Args:
        doi: The DOI to convert
        
    Returns:
        The corresponding PubMed ID
    """
    return await lt.convert_doi_to_pmid(doi)


@mcp.tool()
async def get_article_abstract(identifier: str) -> str:
    """
    Get the abstract of an article by its PMID or DOI.
    
    Args:
        identifier: PMID or DOI of the article
        
    Returns:
        The article abstract
    """
    return await lt.get_article_abstract(identifier)


@mcp.tool()
async def extract_text_from_pdf_url(url: str) -> str:
    """
    Extract text from a PDF at the given URL.
    
    Args:
        url: URL to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    return await lt.extract_text_from_pdf_url(url)


@mcp.tool()
async def search_literature_web(query: str) -> str:
    """
    Search the web for scientific literature.
    
    Args:
        query: The search query
        
    Returns:
        Search results with summaries
    """
    return await lt.search_literature_web(query)


@mcp.tool()
async def retrieve_literature_page(url: str) -> str:
    """
    Fetch the contents of a web page related to scientific literature.
    
    Args:
        url: The URL to fetch
        
    Returns:
        The contents of the web page
    """
    return await lt.retrieve_literature_page(url)


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