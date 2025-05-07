"""
Gradio interface for the PaperQA agent.
"""
from typing import List, Optional, Any

import gradio as gr

from aurelian.utils.async_utils import run_sync
from .paperqa_agent import paperqa_agent
from .paperqa_config import PaperQADependencies, get_config


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
    # Initialize dependencies if needed
    if deps is None:
        deps = get_config()

        # Apply any kwargs to the dependencies
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