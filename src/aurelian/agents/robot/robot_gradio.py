"""
Gradio UI for the ROBOT Ontology agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.robot.robot_ontology_agent import robot_ontology_agent
from aurelian.agents.robot.robot_config import RobotOntologyDependencies
from aurelian.utils.async_utils import run_sync


def chat(deps: Optional[RobotOntologyDependencies] = None, **kwargs):
    """
    Initialize a chat interface for the ROBOT ontology agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = RobotOntologyDependencies()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: robot_ontology_agent.chat(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="ROBOT Ontology AI Assistant",
        examples=[
            ["Create an ontology for snack foods with properties like name, ingredients, and calories"],
            ["Convert the CSV file snacks.csv to OWL"],
            ["Merge my snacks.owl with another ontology"]
        ]
    )