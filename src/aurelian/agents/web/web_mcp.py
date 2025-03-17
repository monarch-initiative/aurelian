"""
MCP tools for web search operations.
"""
import os

from mcp.server.fastmcp import FastMCP

import aurelian.agents.web.web_tools as wt
from aurelian.dependencies.workdir import WorkDir, HasWorkdir
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("web", instructions="Web search operations")


def deps() -> HasWorkdir:
    deps = HasWorkdir()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[HasWorkdir]:
    rc: RunContext[HasWorkdir] = RunContext[HasWorkdir](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use retrieve_web_page tool.

    Args:
        query: Text query

    Returns: 
        Matching web pages plus summaries
    """
    return await wt.search_web(query)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')