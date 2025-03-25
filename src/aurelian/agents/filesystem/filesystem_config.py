"""
Configuration for the Filesystem agent.
"""
import os

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


class FilesystemDependencies(HasWorkdir):
    """
    Filesystem agent dependencies that include a working directory.
    
    This allows the agent to maintain state and access files on the local filesystem.
    """
    pass


def get_config() -> FilesystemDependencies:
    """Get a default configuration for the Filesystem agent.
    
    Returns:
        FilesystemDependencies object with default settings
    """
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None

    return FilesystemDependencies(workdir=workdir)