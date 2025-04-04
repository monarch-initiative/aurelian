"""
Gradio interface for the Gene agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.gene.gene_agent import gene_agent
from aurelian.agents.gene.gene_config import GeneConfig
from aurelian.utils.async_utils import run_sync


def chat(deps: Optional[GeneConfig] = None, **kwargs):
    """
    Initialize a chat interface for the Gene agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = GeneConfig()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: gene_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Gene Information Assistant",
        examples=[
            ["Get description for TP53"],
            ["Get information about the BRCA1 gene"],
            ["Get descriptions for multiple genes: INS, ALB, APOE"],
            ["What is the function of KRAS?"],
            ["Get descriptions for ENSG00000139618, ENSG00000141510"]
        ]
    )