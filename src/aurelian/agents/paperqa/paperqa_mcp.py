"""
MCP tools for working with PaperQA for scientific literature search and analysis.
"""
import os
from typing import Dict, List, Any, Optional

from mcp.server.fastmcp import FastMCP

import aurelian.agents.paperqa.paperqa_tools as pt
from aurelian.agents.paperqa.paperqa_agent import paperqa_agent, PAPERQA_SYSTEM_PROMPT
from aurelian.agents.paperqa.paperqa_config import PaperQADependencies
from pydantic_ai import RunContext

mcp = FastMCP("paperqa", instructions=PAPERQA_SYSTEM_PROMPT.strip())


from aurelian.dependencies.workdir import WorkDir

def deps() -> PaperQADependencies:
    deps = PaperQADependencies()
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/paperqa")
    deps.workdir = WorkDir(loc)
    
    paper_dir = os.getenv("PAPERQA_PAPER_DIRECTORY", os.path.join(loc, "papers"))
    deps.paper_directory = paper_dir
    
    if os.getenv("PAPERQA_LLM"):
        deps.llm = os.getenv("PAPERQA_LLM")
    
    if os.getenv("PAPERQA_EMBEDDING"):
        deps.embedding = os.getenv("PAPERQA_EMBEDDING")
    
    return deps

def ctx() -> RunContext[PaperQADependencies]:
    rc: RunContext[PaperQADependencies] = RunContext[PaperQADependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def search_papers(query: str, max_papers: Optional[int] = None) -> Any:
    """
    Search for papers relevant to the query using PaperQA.
    
    Args:
        query: The search query for scientific papers
        max_papers: Maximum number of papers to return (overrides config)
        
    Returns:
        The search results with paper information
        
    This searches for scientific papers based on your query. It returns papers 
    that are most relevant to the topic you're searching for. You can optionally 
    specify a maximum number of papers to return.
    """
    return await pt.search_papers(ctx(), query, max_papers)


@mcp.tool()
async def query_papers(query: str) -> Any:
    """
    Query the papers to answer a specific question using PaperQA.
    
    Args:
        query: The question to answer based on the papers
        
    Returns:
        Detailed answer with citations from the papers
        
    This tool analyzes the papers in your collection to provide an evidence-based 
    answer to your question. It extracts relevant information from across papers 
    and synthesizes a response with citations to the source papers.
    """
    return await pt.query_papers(ctx(), query)


@mcp.tool()
async def add_paper(path: str, citation: Optional[str] = None) -> Any:
    """
    Add a specific paper to the collection.
    
    Args:
        path: Path to the paper file or URL
        citation: Optional citation for the paper
        
    Returns:
        Information about the added paper
        
    You can add a paper by providing its file path (PDF) or a URL to the paper 
    (must be accessible). The paper will be added to your collection for searching 
    and querying. You can optionally provide a citation string.
    """
    return await pt.add_paper(ctx(), path, citation)

@mcp.tool()
async def add_papers(path: str,) -> Any:
    """
    Add multiple papers to the collection.
    Args:
        path: Path to the paper file or URL
        citation: Optional citation for the paper

    Returns:
        Informations about the added papers

    You can add multiple papers by providing its file path (PDF) or a URL to the
    paper (must be accessible). The paper will be added to your collection for
    searching and querying.
    """
    return await pt.add_papers(ctx(), path)


@mcp.tool()
async def list_papers() -> Any:
    """
    List all papers in the current paper directory.
    
    Args:
        None
        
    Returns:
        Information about all papers in the paper directory
        
    This lists all papers currently in your collection, showing their file paths and 
    any other available metadata. Use this to see what papers you have available 
    for searching and querying.
    """
    return await pt.list_papers(ctx())


@mcp.tool()
async def build_index() -> Any:
    """
    Rebuild the search index for papers.
    
    Args:
        None
        
    Returns:
        Information about the indexing process
        
    This rebuilds the search index for all papers in your paper directory.
    The index is required for searching and querying papers. You should run this
    after adding new papers to make them searchable.
    """
    return await pt.build_index(ctx())


if __name__ == "__main__":
    print("Running the PaperQA MCP server")
    print("Use Ctrl-C to exit")
    mcp.run(transport='stdio')