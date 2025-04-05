"""
MCP tools for creating SVG drawings.
"""
import os
from typing import Dict, List

from mcp.server.fastmcp import FastMCP

import aurelian.agents.draw.draw_tools as dt
from aurelian.agents.draw.draw_agent import SYSTEM
from aurelian.agents.draw.draw_config import DrawDependencies
from pydantic_ai import RunContext

# Initialize FastMCP server
mcp = FastMCP("draw", instructions=SYSTEM)


from aurelian.dependencies.workdir import WorkDir

def deps() -> DrawDependencies:
    deps = DrawDependencies()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[DrawDependencies]:
    rc: RunContext[DrawDependencies] = RunContext[DrawDependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def create_svg_drawing(description: str) -> str:
    """
    Create an SVG drawing based on a text description.

    Args:
        description: Detailed description of what to draw
        
    Returns:
        SVG markup of the drawing
    """
    return await dt.create_svg_drawing(ctx(), description)


@mcp.tool()
async def convert_svg_to_png(svg_content: str) -> bytes:
    """
    Convert SVG content to PNG image.

    Args:
        svg_content: SVG markup as a string
        
    Returns:
        PNG image data as bytes
    """
    return await dt.convert_svg_to_png(ctx(), svg_content)


@mcp.tool()
async def svg_to_data_url(svg_content: str) -> str:
    """
    Convert SVG content to a data URL for embedding in HTML.

    Args:
        svg_content: SVG markup as a string
        
    Returns:
        Data URL representation of the SVG
    """
    return await dt.svg_to_data_url(ctx(), svg_content)


@mcp.tool()
async def judge_drawing(svg_content: str, description: str) -> str:
    """
    Judge the quality of an SVG drawing based on the description.
    
    Args:
        svg_content: SVG markup as a string
        description: The original description of what to draw
        
    Returns:
        Feedback on the drawing's clarity and simplicity
    """
    return await dt.judge_drawing(ctx(), svg_content, description)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')