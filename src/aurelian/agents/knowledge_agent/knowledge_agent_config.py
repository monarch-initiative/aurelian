"""Configuration for the Knowledge Agent."""

from dataclasses import dataclass

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class KnowledgeAgentDependencies(HasWorkdir):
    """Dependencies for the Knowledge Agent.

    This class defines the resources and configurations needed by the Knowledge Agent
    to extract structured knowledge from scientific text.
    """
    pass


def get_config() -> KnowledgeAgentDependencies:
    """Get the configuration for the Knowledge Agent.

    Returns:
        KnowledgeAgentDependencies: Configuration for the Knowledge Agent.
    """
    return KnowledgeAgentDependencies()