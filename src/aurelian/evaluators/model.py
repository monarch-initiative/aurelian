# Use TypedDict for metadata
from typing_extensions import TypedDict


MetadataDict = TypedDict("Metadata", {"difficulty": str, "type": str})


def metadata(difficulty: str, type: str) -> MetadataDict:
    return {"difficulty": difficulty, "type": type}