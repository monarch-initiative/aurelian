"""
Gradio UI for the draw agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.draw.draw_agent import draw_agent
from aurelian.agents.draw.draw_config import DrawDependencies
from aurelian.utils.async_utils import run_sync


def chat(deps: Optional[DrawDependencies] = None, workdir: str = None, **kwargs):
    """
    Initialize a chat interface for the draw agent.
    
    Args:
        deps: Optional dependencies configuration
        workdir: Optional working directory path
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = DrawDependencies()
        
    if workdir:
        deps.workdir.location = workdir

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: draw_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Drawing AI Assistant",
        examples=[
            ["Draw a simple cat face"],
            ["Create an SVG of a tree with birds"],
            ["Draw a basic house with a chimney"]
        ]
    )