"""Knowledge Agent for scientific knowledge extraction."""

from typing import Any
import time

from pydantic_ai import Agent
import logfire

from .knowledge_agent_models import KnowledgeAgentOutput

from aurelian.agents.knowledge_agent.knowledge_agent_config import KnowledgeAgentDependencies
from aurelian.agents.knowledge_agent.knowledge_agent_tools import (
    search_ontology_with_oak,
    generate_and_validate_schema,
    search_ontology_terms
)


def knowledge_agent(model="openai:gpt-4o", deps=None):
    """Initialize the Knowledge Agent.

    Args:
        model: The model to use for the agent
        deps: Dependencies for the agent (KnowledgeAgentDependencies with composed deps)

    Returns:
        Agent: A configured knowledge agent
    """
    # Configure Logfire for this agent
    logfire.configure()
    
    return Agent(
        model,
        deps_type=KnowledgeAgentDependencies,
        result_type=KnowledgeAgentOutput,
        system_prompt="""
        You are an expert curator of scientific knowledge. Your purpose is to take 
        unstructured scientific text and output structured scientific knowledge that is 
        aligned to a schema that describes the knowledge the user wants to extract.  

        ## WORKFLOW:
        1. **If no schema is provided**: Use `generate_and_validate_schema` to create an appropriate LinkML schema first
        2. **Extract entities**: Use the schema to extract structured knowledge from the text
        3. **Ground entities**: Use `search_ontology_terms` to ground entities to standard ontologies

        You will be given some scientific text and either:
        - A LinkML schema (use it directly for extraction)
        - Text only (generate a schema first, then extract)

        You can output as much or as little data as you think is sensible, as long as it is
        supported by the scientific text. 

        The LinkML schema describes the knowledge that the user wants to extract. Pay particular
        attention to entity types and relationships defined in the schema. These describe
        the types of things the user are interested in, and relationships between them.

        The schema may include some advice about what annotators to use when using the 
        search_ontology tool to ground the terms to the schema. For example, the following items
        in the schema mean that you should use the Mondo Disease Ontology to ground disease 
        terms:

        id_prefixes:
          - MONDO
        annotations:
          annotators: sqlite:obo:mondo

        and the following means that you should use the Human Phenotype Ontology: 

        id_prefixes:
        - HP
        annotations:
          annotators: sqlite:obo:hp

        Some other guidelines:
        1. Use the schema to guide your extraction of knowledge from the scientific text.
        2. Ground entities to ontologies using `search_ontology_terms` for precise mapping.
        3. **FOCUS ON RELATIONSHIPS**: Carefully analyze what is connected in the text:
           - Look for causal relationships (X causes Y, X leads to Y)
           - Look for functional relationships (X encodes Y, X participates in Y)
           - Look for therapeutic relationships (X treats Y, X inhibits Y)
           - Look for genetic relationships (mutations in X increase risk of Y)
           - Extract BOTH entities in any relationship you identify
        4. Extract ALL relevant entities from the text - be comprehensive.
        5. **Track grounding sources**: When grounding entities, always populate the `grounding_source` field:
           - `"ontology:mondo"` for MONDO disease ontology
           - `"ontology:hgnc"` for HGNC gene nomenclature
           - `"ontology:hp"` for Human Phenotype Ontology
           - `"ontology:go"` for Gene Ontology
           - `"ontology:chebi"` for chemical entities
           - `"web_search"` for entities grounded via web search
        6. In the "potentially_missing" field, identify important terms that might have been missed:
           - Look for gene names, protein names, drug names that weren't extracted
           - Look for disease subtypes, procedures, biological processes
           - Pay special attention to entities mentioned in relationships
           - Note why each might have been missed (e.g., "not in schema", "complex terminology")
        7. Output structured knowledge in JSON format matching the schema.
        8. Do not respond conversationally, output structured data only.
        """,
        tools=[
            search_ontology_with_oak,
            search_ontology_terms,  # Full ontology mapper agent delegation
            generate_and_validate_schema  # Schema generator with LinkML validation
        ]
    )


def run_sync(prompt: str, deps: KnowledgeAgentDependencies = None, **kwargs) -> Any:
    """Run the Knowledge Agent synchronously with Logfire monitoring.

    Args:
        prompt: The prompt to send to the agent
        deps: Dependencies for the agent
        **kwargs: Additional arguments to pass to the agent

    Returns:
        Any: The result from running the agent
    """
    with logfire.span("knowledge_agent_run", prompt=prompt[:100] + "..." if len(prompt) > 100 else prompt):
        start_time = time.time()
        
        logfire.info("Starting knowledge extraction",
                    prompt_length=len(prompt),
                    model=kwargs.get("model", "openai:gpt-4o"))
        
        try:
            if deps is None:
                from aurelian.agents.knowledge_agent.knowledge_agent_config import get_config
                deps = get_config()
            
            agent = knowledge_agent(model=kwargs.get("model", "openai:gpt-4o"))
            result = agent.run_sync(user_prompt=prompt, deps=deps)
            
            processing_time = time.time() - start_time
            logfire.info("Knowledge extraction completed",
                        processing_time=processing_time,
                        result_type=type(result.output).__name__ if hasattr(result, 'output') else str(type(result)))
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logfire.error("Knowledge extraction failed",
                         error=str(e),
                         processing_time=processing_time)
            raise


knowledge_agent_agent = knowledge_agent()
