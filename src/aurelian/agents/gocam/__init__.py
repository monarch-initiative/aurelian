"""
GOCAM agent module for working with Gene Ontology Causal Activity Models.
"""
from pathlib import Path

THIS_DIR = Path(__file__).parent
DOCUMENTS_DIR = THIS_DIR / "documents"

# isort: skip_file
from .gocam_agent import gocam_agent  # noqa: E402
from .gocam_config import GOCAMDependencies, get_config  # noqa: E402
from .gocam_gradio import chat  # noqa: E402
from .gocam_tools import (  # noqa: E402
    search_gocams,
    lookup_gocam,
    lookup_uniprot_entry,
    all_documents,
    fetch_document,
    validate_gocam_model,
)

__all__ = [
    # Constants
    "THIS_DIR",
    "DOCUMENTS_DIR",
    
    # Agent
    "gocam_agent",
    # Config
    "GOCAMDependencies",
    "get_config",
    
    # Tools
    "search_gocams",
    "lookup_gocam",
    "lookup_uniprot_entry",
    "all_documents",
    "fetch_document",
    "validate_gocam_model",
    
    # Gradio
    "chat",
]