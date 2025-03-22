"""
Gradio UI for the Web agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.dependencies.workdir import HasWorkdir
from aurelian.agents.web.web_mcp import mcp
from aurelian.utils.async_utils import run_sync


def chat(deps: Optional[HasWorkdir] = None, **kwargs):
    """
    Initialize a chat interface for the Web agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        from aurelian.agents.web.web_mcp import deps as get_deps
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
        title="Web Search AI Assistant",
        examples=[
            ["Search for information about gene ontology"],
            ["Find recent research papers on CRISPR"],
            ["Look up information about linkML data modeling"]
        ]
    )