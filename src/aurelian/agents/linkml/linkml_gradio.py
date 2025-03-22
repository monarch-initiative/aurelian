"""
Gradio UI for the LinkML agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.linkml.linkml_agent import linkml_agent
from aurelian.agents.linkml.linkml_config import LinkMLDependencies
from aurelian.utils.async_utils import run_sync


def chat(deps: Optional[LinkMLDependencies] = None, **kwargs):
    """
    Initialize a chat interface for the LinkML agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = LinkMLDependencies()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: linkml_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="LinkML AI Assistant",
        examples=[
            ["Generate a schema for modeling the chemical components of foods"],
            ["Generate a schema for this data: {name: 'joe', age: 22}"],
        ]
    )