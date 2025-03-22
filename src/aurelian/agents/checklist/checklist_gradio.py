"""
Gradio interface for the Checklist agent.
"""
from typing import List, Optional

import gradio as gr

from .checklist_agent import checklist_agent
from .checklist_config import ChecklistDependencies, get_config
from aurelian.utils.async_utils import run_sync


async def get_info(query: str, history: List[str], deps: ChecklistDependencies) -> str:
    """
    Process a query using the checklist agent.
    
    Args:
        query: The user query
        history: The conversation history
        deps: The dependencies configuration
        
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
    result = await checklist_agent.run(query, deps=deps)
    return result.data


def chat(deps: Optional[ChecklistDependencies] = None, **kwargs):
    """
    Create a Gradio chat interface for the Checklist agent.
    
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
        return run_sync(lambda: get_info(query, history, deps))
    
    return gr.ChatInterface(
        fn=get_info_wrapper,
        type="messages",
        title="Checklist AI Assistant",
        examples=[
            ["Evaluate https://journals.asm.org/doi/10.1128/mra.01361-19 using STREAMS"],
            [
                (
                    "Check the paper 'Exploration of the Biosynthetic Potential of the Populus Microbiome'"
                    " https://journals.asm.org/doi/10.1128/msystems.00045-18"
                )
            ],
        ],
    )