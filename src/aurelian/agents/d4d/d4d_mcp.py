"""
MCP tools for the D4D (Datasheets for Datasets) agent.
"""
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from aurelian.agents.d4d.d4d_agent import data_sheets_agent
from aurelian.agents.d4d.d4d_config import D4DConfig
import aurelian.agents.d4d.d4d_tools as dt
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("d4d", instructions="Datasheets for Datasets (D4D) agent")


from aurelian.dependencies.workdir import WorkDir

def deps() -> D4DConfig:
    deps = D4DConfig()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[D4DConfig]:
    rc: RunContext[D4DConfig] = RunContext[D4DConfig](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.system_prompt
async def add_schema() -> str:
    """Add the full schema to the system prompt."""
    return await dt.get_full_schema(ctx())


@mcp.tool()
async def get_full_schema(url: Optional[str] = None) -> str:
    """
    Load the full datasheets for datasets schema from GitHub.
    
    Args:
        url: Optional URL override for the schema location
        
    Returns:
        The schema text content
    """
    return await dt.get_full_schema(ctx(), url)


@mcp.tool()
async def process_website_or_pdf(url: str) -> str:
    """
    Process a website or PDF with dataset information.
    
    Args:
        url: URL to a website or PDF file with dataset information
        
    Returns:
        YAML formatted dataset metadata following the D4D schema
    """
    return await dt.process_website_or_pdf(ctx(), url)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')