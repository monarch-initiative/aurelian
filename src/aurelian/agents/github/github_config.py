"""
Configuration for the GitHub agent.
"""
import os

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


class GitHubDependencies(HasWorkdir):
    """
    GitHub agent dependencies that include a working directory.
    
    This allows the agent to maintain state and access files on the local filesystem.
    """
    pass


def get_config() -> GitHubDependencies:
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None

    return GitHubDependencies(workdir=workdir)