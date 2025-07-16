"""
Configuration for schema generator agent.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class SchemaGeneratorDependencies(HasWorkdir):
    """Dependencies for sophisticated schema generation.
    
    Uses dependency injection pattern - LinkML dependencies are injected when needed.
    """
    
    workdir: WorkDir = field(default_factory=lambda: WorkDir("/tmp/aurelian"))
    
    include_grounding: bool = field(
        default=True,
        metadata={"description": "Include ontology grounding in schemas"}
    )
    include_examples: bool = field(
        default=True,
        metadata={"description": "Include examples in generated schemas"}
    )
    max_schema_complexity: str = field(
        default="high",
        metadata={"description": "Schema complexity level: low, medium, high"}
    )
    default_prefixes: Dict[str, str] = field(
        default_factory=lambda: {
            "linkml": "https://w3id.org/linkml/",
            "biolink": "https://w3id.org/biolink/",
            "GO": "http://purl.obolibrary.org/obo/GO_",
            "MONDO": "http://purl.obolibrary.org/obo/MONDO_",
            "CHEBI": "http://purl.obolibrary.org/obo/CHEBI_",
            "HGNC": "http://purl.obolibrary.org/obo/HGNC_",
            "CL": "http://purl.obolibrary.org/obo/CL_"
        },
        metadata={"description": "Default prefixes for schemas"}
    )


def get_config() -> SchemaGeneratorDependencies:
    """Get default schema generator configuration."""
    return SchemaGeneratorDependencies()


def get_linkml_deps():
    """Get LinkML dependencies via dependency injection."""
    from aurelian.agents.linkml.linkml_config import get_config as get_linkml_config
    return get_linkml_config()