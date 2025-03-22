"""
Gradio interface for the Biblio agent.
"""
from typing import List, Optional

import gradio as gr

from .biblio_agent import biblio_agent
from .biblio_config import BiblioDependencies, get_config


async def get_info(query: str, history: List[str], deps: BiblioDependencies) -> str:
    """
    Process a query using the biblio agent.
    
    Args:
        query: The user query
        history: The conversation history
        deps: The dependencies for the agent
        
    Returns:
        The agent's response
    """
    print(f"QUERY: {query}")
    print(f"HISTORY: {history}")
    
    # Add history to the query if available
    if history:
        query += "## History"
        for h in history:
            query += f"\n{h}"
    
    # Run the agent
    result = await biblio_agent.run(query, deps=deps)
    return result.data


def chat(deps: Optional[BiblioDependencies] = None, **kwargs):
    """
    Create a Gradio chat interface for the Biblio agent.
    
    Args:
        deps: Optional dependencies configuration
        kwargs: Additional keyword arguments for the agent
        
    Returns:
        A Gradio ChatInterface
    """
    if deps is None:
        deps = get_config()
        
    def get_info_wrapper(query: str, history: List[str]) -> str:
        # Use run_sync to handle the async function
        from aurelian.utils.async_utils import run_sync
        return run_sync(lambda: get_info(query, history, deps))
    
    return gr.ChatInterface(
        fn=get_info_wrapper,
        type="messages",
        title="Biblio AI Assistant",
        examples=[
            ["What patients have liver disease?"],
            ["What biblio involve genes from metabolic pathways"],
            ["How does the type of variant affect phenotype in peroxisomal disorders?"],
            ["Examine biblio for skeletal dysplasias, check them against publications"],
        ],
    )