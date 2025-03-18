"""
MCP tools for filesystem operations.
"""
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

import aurelian.agents.filesystem.filesystem_tools as ft
from aurelian.dependencies.workdir import WorkDir, HasWorkdir
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("filesystem", instructions="Filesystem operations")


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
async def inspect_file(data_file: str) -> str:
    """
    Inspect a file in the working directory.

    Args:
        data_file: name of file

    Returns:
        Contents of the file
    """
    return await ft.inspect_file(ctx(), data_file)


@mcp.tool()
async def download_url_as_markdown(url: str, local_file_name: str) -> ft.DownloadResult:
    """
    Download a URL and convert to markdown.

    Args:
        url: The URL to download
        local_file_name: The name to save the file as

    Returns:
        DownloadResult with file name and number of lines
    """
    return await ft.download_url_as_markdown(ctx(), url, local_file_name)


@mcp.tool()
async def list_files() -> str:
    """
    List files in the working directory.

    Returns:
        A string listing the files in the working directory
    """
    return await ft.list_files(ctx())


@mcp.tool()
async def write_to_file(file_name: str, data: str) -> str:
    """
    Write data to a file in the working directory.

    Args:
        file_name: Name of file to write
        data: Data to write to the file

    Returns:
        Confirmation message
    """
    return await ft.write_to_file(ctx(), file_name, data)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')