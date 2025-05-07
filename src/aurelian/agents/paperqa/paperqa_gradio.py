"""
Gradio interface for the PaperQA agent.
"""
from typing import List, Optional, Any

import gradio as gr

from aurelian.utils.async_utils import run_sync
from .paperqa_agent import paperqa_agent
from .paperqa_config import PaperQADependencies, get_config


async def get_info(query: str, history: List[str], deps: PaperQADependencies, model=None) -> str:
    """
    Process a query using the PaperQA agent.
    
    Args:
        query: The user query
        history: The conversation history
        deps: The dependencies for the agent
        model: Optional model override
        
    Returns:
        The agent's response
    """
    print(f"QUERY: {query}")
    print(f"HISTORY: {history}")
    
    if history:
        query += "\n\n## Previous Conversation:\n"
        for h in history:
            query += f"\n{h}"
    
    result = await paperqa_agent.run(query, deps=deps, model=model)
    return result.data


def chat(deps: Optional[PaperQADependencies] = None, model=None, **kwargs):
    """
    Create a Gradio chat interface for the PaperQA agent.

    Args:
        deps: Optional dependencies configuration
        model: Optional model override
        kwargs: Additional keyword arguments for dependencies

    Returns:
        A Gradio ChatInterface
    """
    if deps is None:
        deps = get_config()

        for key, value in kwargs.items():
            if hasattr(deps, key):
                setattr(deps, key, value)

    def get_info_wrapper(query: str, history: List[str]) -> str:
        """Wrapper for the async get_info function."""
        import asyncio
        return asyncio.run(get_info(query, history, deps, model))

    return gr.ChatInterface(
        fn=get_info_wrapper,
        type="messages",
        title="PaperQA AI Assistant",
        description="""This assistant helps you search and analyze scientific papers. You can:
        - Search for papers on a topic
        - Ask questions about the papers in the repository
        - Add specific papers by path or URL
        - List all papers in the collection""",
        examples=[
            ["Search for papers on CRISPR gene editing"],
            ["What are the main challenges in CRISPR gene editing?"],
            ["What is the relationship between CRISPR and Cas9?"],
        ],
    )