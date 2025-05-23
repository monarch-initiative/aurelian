"""
Configuration for the Web agent.
"""
import os

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


class WebDependencies(HasWorkdir):
    """
    Web agent dependencies that include a working directory.
    
    This allows the agent to maintain state and access files on the local filesystem.
    """
    pass


def get_config() -> WebDependencies:
    """Get a default configuration for the Web agent.
    
    Returns:
        WebDependencies object with default settings
    """
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None

    return WebDependencies(workdir=workdir)