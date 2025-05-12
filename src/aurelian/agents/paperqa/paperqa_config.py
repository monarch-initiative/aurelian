"""
Configuration for the PaperQA agent.
"""
import warnings
from dataclasses import dataclass, field
import os
from typing import Optional, List

from paperqa import Settings as PQASettings
from paperqa.settings import (
    AnswerSettings,
    ParsingSettings,
    PromptSettings,
    AgentSettings,
    IndexSettings,
)

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class PaperQADependencies(HasWorkdir):
    """Configuration for the PaperQA agent."""

    # Paper directory settings
    paper_directory: str = field(
        default_factory=lambda: os.getcwd(),
        metadata={"description": "Directory containing papers to be searched"}
    )
    index_name: Optional[str] = field(
        default=None,
        metadata={"description": "Optional name for the search index. If None, it will be generated based on settings."}
    )

    # Model settings - These are PaperQA defaults
    llm: str = field(
        default="gpt-4o-2024-11-20",
        metadata={"description": "LLM to use for queries and answer generation. Default is gpt-4o-2024-11-20."}
    )
    summary_llm: str = field(
        default="gpt-4o-2024-11-20",
        metadata={"description": "LLM to use for summarization. Default is gpt-4o-2024-11-20."}
    )
    embedding: str = field(
        default="text-embedding-3-small",
        metadata={"description": "Embedding model to use. Default is text-embedding-3-small."}
    )
    temperature: float = field(
        default=0.1,
        metadata={"description": "Temperature for LLM generation. Default is 0.1."}
    )

    # Search settings - PaperQA default
    search_count: int = field(
        default=8,
        metadata={"description": "Number of papers to retrieve in searches. Default is 8."}
    )

    # Answer settings - PaperQA defaults
    evidence_k: int = field(
        default=10,
        metadata={"description": "Number of evidence pieces to retrieve. Default is 10."}
    )
    answer_max_sources: int = field(
        default=5,
        metadata={"description": "Maximum number of sources to use in answers. Default is 5."}
    )
    max_concurrent_requests: int = field(
        default=4,
        metadata={"description": "Maximum number of concurrent requests to LLMs. Default is 4."}
    )

    # Parsing settings - PaperQA defaults
    chunk_size: int = field(
        default=5000,
        metadata={"description": "Size of document chunks for embedding. Default is 5000."}
    )
    overlap: int = field(
        default=250,
        metadata={"description": "Overlap between chunks. Default is 250."}
    )

    workdir: Optional[WorkDir] = None

    def __post_init__(self):
        """Initialize the config with default values."""
        if self.workdir is None:
            self.workdir = WorkDir()

    def set_paperqa_settings(self,
                             paper_directory) -> PQASettings:
        """
        Convert to PaperQA Settings object.

        This allows users to customize all PaperQA settings through the dependencies object.
        Any changes to the dependencies will be reflected in the returned Settings object.

        Args:
            paper_directory (str): Directory containing papers to be indexed or queried against.
        """

        return PQASettings(
            llm=self.llm,
            summary_llm=self.summary_llm,
            embedding=self.embedding,
            temperature=self.temperature,

            answer=AnswerSettings(
                evidence_k=self.evidence_k,
                answer_max_sources=self.answer_max_sources,
                max_concurrent_requests=self.max_concurrent_requests,
            ),

            parsing=ParsingSettings(
                chunk_size=self.chunk_size,
                overlap=self.overlap,
            ),

            agent=AgentSettings(
                agent_llm=self.llm,
                search_count=self.search_count,
                index=IndexSettings(
                    name=self.index_name,
                    paper_directory=paper_directory
                ),
            ),
        )


def get_config(paper_directory) -> PaperQADependencies:
    """
    Get the PaperQA configuration from environment variables or defaults.

    Args:
        paper_directory (str): Directory containing papers to be indexed or queried against.

    Returns:
        A PaperQADependencies instance with default settings.

    Note:
        Users can modify the returned object to customize settings.
        Example:
            ```python
            deps = get_config(paper_directory="/path/to/papers")
            deps.llm = "claude-3-sonnet-20240229"  # Use Claude instead of default GPT-4
            deps.temperature = 0.5  # Increase temperature
            deps.evidence_k = 15  # Retrieve more evidence
            ```
    """

    if not os.path.exists(paper_directory):
        warnings.warn(f"Paper directory does not exist: {paper_directory}. Creating it.")
        os.makedirs(paper_directory, exist_ok=True)

    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None

    # Get embedding model from environment if available
    embedding = os.environ.get("PAPERQA_EMBEDDING", "text-embedding-3-small")

    # Get LLM from environment if available
    llm = os.environ.get("PAPERQA_LLM", "gpt-4o-2024-11-20")

    return PaperQADependencies(
        paper_directory=paper_directory,
        workdir=workdir,
        embedding=embedding,
        llm=llm,
    )
