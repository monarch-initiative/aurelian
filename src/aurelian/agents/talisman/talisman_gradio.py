"""
Gradio interface for the Talisman agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.agents.talisman.talisman_agent import talisman_agent
from aurelian.agents.talisman.talisman_config import TalismanConfig
from aurelian.utils.async_utils import run_sync


def chat(deps: Optional[TalismanConfig] = None, **kwargs):
    """
    Initialize a chat interface for the Talisman agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = TalismanConfig()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: talisman_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Talisman Gene Analysis Assistant",
        examples=[
            ["Get description for TP53"],
            ["Get information about the BRCA1 gene"],
            ["Get descriptions for multiple genes: INS, ALB, APOE"],
            ["What is the function of KRAS?"],
            ["Analyze the relationship between TP53 and MDM2"],
            ["Analyze these genes and their functional relationships: BRCA1, BRCA2, ATM, PARP1"],
            ["Get descriptions for ENSG00000139618, ENSG00000141510"]
        ]
    )