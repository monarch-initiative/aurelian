"""
GO Annotation Review agent module for reviewing GO standard annotations.
"""
from pathlib import Path

THIS_DIR = Path(__file__).parent
DOCUMENTS_DIR = THIS_DIR / "documents"

__all__ = [
    # Constants
    "THIS_DIR",
    "DOCUMENTS_DIR",
]