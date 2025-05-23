"""
MCP tools for working with bibliographies and citation data.
"""
import os
from typing import Dict, List

from mcp.server.fastmcp import FastMCP

import aurelian.agents.biblio.biblio_tools as bt
from aurelian.agents.biblio.biblio_agent import biblio_agent
from aurelian.agents.biblio.biblio_config import BiblioDependencies
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("biblio", instructions=biblio_agent.system_prompt)


from aurelian.dependencies.workdir import WorkDir

def deps() -> BiblioDependencies:
    deps = BiblioDependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[BiblioDependencies]:
    rc: RunContext[BiblioDependencies] = RunContext[BiblioDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def search_bibliography(query: str) -> List[Dict]:
    """
    Performs a retrieval search over the biblio database.

    Args:
        query: The search query (disease, phenotype, gene, etc.)
        
    Returns:
        A list of biblio objects matching the query

    The query can be any text, such as name of a disease, phenotype, gene, etc.

    The objects returned are "biblio" which is a structured representation
    of a patient. Each is uniquely identified by a phenopacket ID (essentially
    the patient ID).

    The objects returned are summaries of biblio; omit some details such
    as phenotypes. Use `lookup_biblio` to retrieve full details of a phenopacket.

    Note that the phenopacket store may not be complete, and the retrieval
    method may be imperfect
    """
    return await bt.search_bibliography(ctx(), query)


@mcp.tool()
async def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.

    Args:
        pmid: The PubMed ID to look up (format: "PMID:nnnnnnn")
        
    Returns:
        The full text if available, otherwise abstract

    A PMID should be of the form "PMID:nnnnnnn" (no underscores).

    NOTE: Phenopacket IDs are typically of the form PMID_nnn_PatientNumber,
    but this should be assumed. To reliably get PMIDs for a phenopacket,
    use `lookup_phenopacket` to retrieve examine the `externalReferences`
    field.
    """
    return await bt.lookup_pmid(ctx(), pmid)


@mcp.tool()
async def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Args:
        query: The search query
        
    Returns:
        Matching web pages plus summaries

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.
    """
    return await bt.search_web(ctx(), query)


@mcp.tool()
async def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Args:
        url: The URL to fetch
        
    Returns:
        The contents of the web page
    """
    return await bt.retrieve_web_page(ctx(), url)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')