"""
Configuration for the Talisman agent.
"""
from dataclasses import dataclass, field
import os
from typing import Any, Dict, Optional

from bioservices import UniProt
from bioservices.eutils import EUtils as NCBI

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class TalismanConfig(HasWorkdir):
    """Configuration for the Talisman agent."""

    # Options for the bioservices UniProt client
    uniprot_client_options: Dict[str, Any] = field(default_factory=dict)
    
    # Options for the bioservices NCBI client
    ncbi_client_options: Dict[str, Any] = field(default_factory=dict)
    
    # OpenAI API key for LLM-based analysis
    openai_api_key: Optional[str] = None
    
    # Model to use for gene set analysis
    model_name: str = "gpt-4o"

    def __post_init__(self):
        """Initialize the config with default values."""
        # Initialize with default options if none provided
        if self.uniprot_client_options is None or len(self.uniprot_client_options) == 0:
            self.uniprot_client_options = {"verbose": False}
            
        if self.ncbi_client_options is None or len(self.ncbi_client_options) == 0:
            self.ncbi_client_options = {"verbose": False, "email": "MJoachimiak@lbl.gov"}
        
        # Initialize the workdir if not already set
        if self.workdir is None:
            self.workdir = WorkDir()
        
        # Try to get OpenAI API key from environment if not provided
        if self.openai_api_key is None:
            import os
            self.openai_api_key = os.environ.get("OPENAI_API_KEY")

    def get_uniprot_client(self) -> UniProt:
        """Get a configured UniProt client."""
        return UniProt(**self.uniprot_client_options)
        
    def get_ncbi_client(self) -> NCBI:
        """Get a configured NCBI client."""
        return NCBI(**self.ncbi_client_options)


def get_config() -> TalismanConfig:
    """Get the Talisman configuration from environment variables or defaults."""
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    return TalismanConfig(
        workdir=workdir,
        uniprot_client_options={"verbose": False},
        ncbi_client_options={"verbose": False}
    )