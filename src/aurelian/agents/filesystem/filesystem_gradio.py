"""
Gradio UI for the Filesystem agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.dependencies.workdir import HasWorkdir
from aurelian.agents.filesystem.filesystem_tools import inspect_file, download_url_as_markdown
from aurelian.agents.filesystem.filesystem_mcp import mcp
from aurelian.utils.async_utils import run_sync


def chat(deps: Optional[HasWorkdir] = None, **kwargs):
    """
    Initialize a chat interface for the Filesystem agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        from aurelian.agents.filesystem.filesystem_mcp import deps as get_deps
        deps = get_deps()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        # Use MCP for the agent
        result = run_sync(lambda: mcp.query(query))
        return result

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Filesystem AI Assistant",
        examples=[
            ["List all files in the working directory"],
            ["Download https://example.com and save as example.md"],
            ["Show me the contents of the file example.md"]
        ]
    )