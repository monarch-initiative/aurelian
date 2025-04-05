"""
Gradio interface for the GO Annotation Review agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.goann.goann_agent import goann_agent
from aurelian.agents.goann.goann_config import GOAnnotationDependencies, get_config
from aurelian.utils.async_utils import run_sync


def chat(deps: Optional[GOAnnotationDependencies] = None, **kwargs):
    """
    Initialize a chat interface for the GO Annotation Review agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = get_config()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: goann_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="GO Annotation Review Assistant",
        description="I can help review GO annotations, check annotation quality, and ensure compliance with GO guidelines.",
        examples=[
            ["Review GO annotations for human NOTCH1 (P46531)"],
            ["Explain the difference between DNA-binding transcription factors and coregulators"],
            ["What are the guidelines for annotating transcription factors?"],
            ["Check if P46531 is correctly annotated as a DNA-binding transcription factor"],
            ["Find GO annotations from PMID:12345678 and assess their quality"],
            ["What evidence codes are most reliable for transcription factor annotations?"],
        ],
    )


def launch_demo():
    """
    Launch the Gradio demo for the GO Annotation Review agent.
    """
    demo = chat()
    demo.launch()


if __name__ == "__main__":
    launch_demo()