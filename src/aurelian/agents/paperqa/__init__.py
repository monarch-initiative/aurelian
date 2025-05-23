"""
PaperQA agent package for scientific literature search and analysis.
"""

# isort: skip_file
from .paperqa_agent import paperqa_agent  # noqa: E402
from .paperqa_config import PaperQADependencies, get_config  # noqa: E402
from .paperqa_gradio import chat  # noqa: E402
from .paperqa_tools import (  # noqa: E402
    search_papers,
    query_papers,
    add_paper,
    add_papers,
    list_papers,
)

__all__ = [
    "paperqa_agent",
    "PaperQADependencies",
    "get_config",
    "search_papers",
    "query_papers",
    "add_paper",
    "add_papers",
    "list_papers",
    "chat",
]