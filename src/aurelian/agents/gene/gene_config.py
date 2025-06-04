"""Configuration for the Gene Agent."""

from dataclasses import dataclass

from aurelian.dependencies.workdir import HasWorkdir


@dataclass
class GeneDependencies(HasWorkdir):
    """Dependencies for the Gene Agent.

    This class defines the resources and configurations needed by the Gene Agent
    to retrieve gene descriptions.
    """
    pass


def get_config() -> GeneDependencies:
    """Get the configuration for the Gene Agent.

    Returns:
        GeneDependencies: Configuration for the Gene Agent.
    """
    return GeneDependencies()