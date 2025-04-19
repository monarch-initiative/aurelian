"""
Configuration classes for the draw agent.
"""
from dataclasses import dataclass
from typing import Optional

from aurelian.dependencies.workdir import HasWorkdir


@dataclass
class DrawDependencies(HasWorkdir):
    """
    Configuration for the draw agent.
    """
    max_svg_size: int = 1024 * 1024  # 1MB max SVG size
    judge_feedback: bool = True  # Whether to get judge feedback


def get_config() -> DrawDependencies:
    """
    Get the Draw agent configuration.
    
    Returns:
        DrawDependencies: The draw dependencies
    """
    return DrawDependencies()