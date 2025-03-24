"""
Configuration for the OAK agent.
"""
import os

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


class OakDependencies(HasWorkdir):
    """
    OAK agent dependencies that include a working directory.
    
    This allows the agent to maintain state and access files on the local filesystem.
    """
    pass


def get_config() -> OakDependencies:
    """Get a default configuration for the OAK agent.
    
    Returns:
        OakDependencies object with default settings
    """
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None

    return OakDependencies(workdir=workdir)