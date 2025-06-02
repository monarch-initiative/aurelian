"""
Configuration for the SPIRES agent.
"""
from dataclasses import dataclass, field
import os
from typing import Optional, Dict, Any

from aurelian.dependencies.workdir import HasWorkdir, WorkDir
from aurelian.agents.paperqa.paperqa_config import PaperQADependencies


@dataclass
class SPIRESDependencies(HasWorkdir):
    """Configuration for the SPIRES agent."""

    # Required parameters (without defaults) must come first
    template_name: str = field(
        default="biological_process.BiologicalProcess",
        metadata={"description": "OntoGPT template to use for extraction. Options: biological_process.BiologicalProcess, gocam.GoCamAnnotations, drug.DrugMechanism, human_phenotype.HumanPhenotype"}
    )
    
    model: str = field(
        default="gpt-4o",
        metadata={"description": "LLM model to use for SPIRES extraction. Should match PaperQA model for consistency."}
    )
    
    model_provider: str = field(
        default="openai",
        metadata={"description": "Model provider. Options: openai, azure, ollama. Should match PaperQA provider."}
    )
    
    temperature: float = field(
        default=0.1,
        metadata={"description": "Temperature for LLM generation. Default is 0.1."}
    )
    
    enable_grounding: bool = field(
        default=True,
        metadata={"description": "Enable entity grounding to ontologies. Default is True."}
    )
    
    chunk_by_sentence: bool = field(
        default=True,
        metadata={"description": "Whether to chunk large text by sentences. Default is True."}
    )
    
    max_tokens: int = field(
        default=4000,
        metadata={"description": "Maximum tokens per chunk when processing large texts. Default is 4000."}
    )
    
    # PaperQA integration
    paperqa_deps: Optional[PaperQADependencies] = field(
        default=None,
        metadata={"description": "PaperQA dependencies for integration. If provided, enables query_paperqa_and_extract tool."}
    )
    
    workdir: Optional[WorkDir] = None

    def __post_init__(self):
        """Initialize the config with default values."""
        if self.workdir is None:
            self.workdir = WorkDir()
        
        # Initialize PaperQA dependencies if not provided
        if self.paperqa_deps is None:
            self.paperqa_deps = PaperQADependencies(workdir=self.workdir)

    def get_engine_kwargs(self) -> Dict[str, Any]:
        """Get keyword arguments for SPIRESEngine initialization."""
        return {
            "model": self.model,
            "model_provider": self.model_provider,
            "temperature": self.temperature,
        }



def get_config() -> SPIRESDependencies:
    """
    Get the SPIRES configuration from environment variables or defaults.

    Returns:
        A SPIRESDependencies instance with default settings.

    Environment Variables:
        SPIRES_TEMPLATE: Template name to use
        SPIRES_MODEL: Model to use
        SPIRES_MODEL_PROVIDER: Model provider
        SPIRES_TEMPERATURE: Temperature for generation
        SPIRES_ENABLE_GROUNDING: Enable entity grounding (true/false)
        AURELIAN_WORKDIR: Working directory path

    Example:
        ```python
        deps = get_config()
        deps.template_name = "drug.DrugMechanism"  # Switch to drug template
        deps.enable_grounding = False  # Disable grounding for speed
        ```
    """
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None

    return SPIRESDependencies(
        template_name=os.environ.get("SPIRES_TEMPLATE"),
        model=os.environ.get("SPIRES_MODEL") or "gpt-4o", 
        model_provider=os.environ.get("SPIRES_MODEL_PROVIDER") or "openai",
        temperature=float(os.environ.get("SPIRES_TEMPERATURE", "0.1")),
        enable_grounding=os.environ.get("SPIRES_ENABLE_GROUNDING", "true").lower() == "true",
        workdir=workdir,
    )