"""
Configuration for the Scientific Knowledge Extraction agent.
"""
from dataclasses import dataclass
import os

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class ScientificKnowledgeExtractionDependencies(HasWorkdir):
    """Configuration for the Scientific Knowledge Extraction agent."""
    
    # Directory containing PDF files to process
    pdf_directory: str = "."
    
    # Directory for output knowledge graph files
    output_directory: str = None
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.workdir is None:
            self.workdir = WorkDir()
            
        # Set default output directory if not provided
        if self.output_directory is None:
            self.output_directory = os.path.join(str(self.workdir.location), "kg_output")
            
        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)


def get_config() -> ScientificKnowledgeExtractionDependencies:
    """Get the Scientific Knowledge Extraction configuration with default settings."""
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    pdf_directory = os.environ.get("AURELIAN_PDF_DIR", ".")
    output_directory = os.environ.get("AURELIAN_KG_OUTPUT_DIR", None)
    
    return ScientificKnowledgeExtractionDependencies(
        workdir=workdir,
        pdf_directory=pdf_directory,
        output_directory=output_directory
    )