"""Configuration for the Aggregator Agent."""

from dataclasses import dataclass

from aurelian.dependencies.workdir import HasWorkdir


@dataclass
class AggregatorDependencies(HasWorkdir):
    """Dependencies for the Aggregator Agent.

    This class defines the resources and configurations needed by the Aggregator Agent.
    """
    pass


def get_config() -> AggregatorDependencies:
    """Get the configuration for the Aggregator Agent.

    Returns:
        AggregatorDependencies: Configuration for the Aggregator Agent.
    """
    return AggregatorDependencies()