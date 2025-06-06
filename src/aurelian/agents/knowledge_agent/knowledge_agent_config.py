"""Configuration for the Knowledge Agent."""

from dataclasses import dataclass
from typing import Optional, List

from aurelian.dependencies.workdir import HasWorkdir, WorkDir
from aurelian.agents.ontology_mapper.ontology_mapper_config import OntologyMapperDependencies


@dataclass
class KnowledgeAgentDependencies(HasWorkdir):
    """Dependencies for the Knowledge Agent.

    This class composes dependencies from delegated agents to ensure efficient
    dependency reuse as per PydanticAI best practices. When delegating to 
    ontology_mapper_agent or schema_generator_agent, we pass these same
    dependencies to avoid creating new connections each time.
    """
    ontology_mapper: OntologyMapperDependencies = None
    schema_generator: "SchemaGeneratorDependencies" = None  # Forward reference
    
    def __post_init__(self):
        """Initialize composed dependencies."""
        if self.workdir is None:
            self.workdir = WorkDir()
            
        if self.ontology_mapper is None:
            self.ontology_mapper = OntologyMapperDependencies(workdir=self.workdir)
            
        if self.schema_generator is None:
            from aurelian.agents.schema_generator.schema_config import SchemaGeneratorDependencies
            self.schema_generator = SchemaGeneratorDependencies(workdir=self.workdir)


def get_config(ontologies: Optional[List[str]] = None) -> KnowledgeAgentDependencies:
    """Get the configuration for the Knowledge Agent.

    Args:
        ontologies: Optional list of ontologies for ontology mapper
        
    Returns:
        KnowledgeAgentDependencies: Composed configuration.
    """
    from aurelian.agents.ontology_mapper.ontology_mapper_config import get_config as get_ontology_config
    
    ontology_config = get_ontology_config(ontologies=ontologies)
    
    config = KnowledgeAgentDependencies(
        workdir=ontology_config.workdir,
        ontology_mapper=ontology_config
    )
    
    return config