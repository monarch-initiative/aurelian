"""
Configuration for the Gene agent.
"""
from dataclasses import dataclass, field
import os
from typing import Any, Dict, Optional

from bioservices import UniProt

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class GeneConfig(HasWorkdir):
    """Configuration for the Gene agent."""

    # Options for the bioservices UniProt client
    uniprot_client_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the config with default values."""
        # Initialize with default options if none provided
        if self.uniprot_client_options is None or len(self.uniprot_client_options) == 0:
            self.uniprot_client_options = {"verbose": False}
        
        # Initialize the workdir if not already set
        if self.workdir is None:
            self.workdir = WorkDir()

    def get_uniprot_client(self) -> UniProt:
        """Get a configured UniProt client."""
        return UniProt(**self.uniprot_client_options)


def get_config() -> GeneConfig:
    """Get the Gene configuration from environment variables or defaults."""
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    return GeneConfig(
        workdir=workdir,
        uniprot_client_options={"verbose": False}
    )