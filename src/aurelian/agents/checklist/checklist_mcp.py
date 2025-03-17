"""
MCP tools for validating papers against checklists.
"""
import os
from typing import Dict, List

from mcp.server.fastmcp import FastMCP

import aurelian.agents.checklist.checklist_tools as ct
from aurelian.agents.checklist.checklist_agent import checklist_agent
from aurelian.agents.checklist.checklist_config import ChecklistDependencies
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("checklist", instructions=checklist_agent.system_prompt)


from aurelian.dependencies.workdir import WorkDir

def deps() -> ChecklistDependencies:
    deps = ChecklistDependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[ChecklistDependencies]:
    rc: RunContext[ChecklistDependencies] = RunContext[ChecklistDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.system_prompt
def add_checklists():
    """Add available checklists to the system prompt."""
    meta = ct.all_checklists()
    return "\n".join([f"- {c['id']}: {c['title']}" for c in meta["checklists"]])


@mcp.tool()
async def retrieve_text_from_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.

    Args:
        pmid: The PubMed ID to look up
        
    Returns: 
        Full text if available, otherwise abstract
    """
    return await ct.retrieve_text_from_pmid(ctx(), pmid)


@mcp.tool()
async def retrieve_text_from_doi(doi: str) -> str:
    """
    Lookup the text of a DOI.

    Args:
        doi: The DOI to look up
        
    Returns: 
        Full text if available, otherwise abstract
    """
    return await ct.retrieve_text_from_doi(ctx(), doi)


@mcp.tool()
async def fetch_checklist(checklist_id: str) -> str:
    """
    Lookup the checklist entry for a given checklist accession number.

    Args:
        checklist_id: The checklist ID (e.g. STREAM, STORMS, ARRIVE)
        
    Returns:
        The content of the checklist
    """
    return await ct.fetch_checklist(ctx(), checklist_id)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')