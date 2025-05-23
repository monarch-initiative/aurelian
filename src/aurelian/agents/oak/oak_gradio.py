"""
Gradio UI for the OAK agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.dependencies.workdir import HasWorkdir
from aurelian.utils.async_utils import run_sync
from pydantic_ai import Agent, Tool

# Create an Agent
oak_agent = Agent(
    model="openai:gpt-4o",
    deps_type=HasWorkdir,
    system_prompt="""
    You are an expert OAK (Ontology Access Kit) assistant. You can help users interact with ontology databases,
    search ontologies, and perform common ontology operations.
    Always provide clear explanations of what you're doing.
    """,
    tools=[]  # OAK tools would be added here
)

def chat(deps: Optional[HasWorkdir] = None, **kwargs):
    """
    Initialize a chat interface for the OAK agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = HasWorkdir()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: oak_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="OAK AI Assistant",
        examples=[
            ["Search for 'diabetes' in the Human Phenotype Ontology"],
            ["Find terms related to 'heart' in GO"],
            ["Get information about the term 'HP:0001250'"]
        ]
    )