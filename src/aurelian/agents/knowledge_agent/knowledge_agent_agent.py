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
    search_ontology_terms,
    ground_entities_with_template_annotators
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
        1. **Extract entities**: Use the schema to extract structured knowledge from the text
        2. **Ground entities**: Use `search_ontology_terms` and 
        `search_ontology_with_oak` to ground entities to standard ontologies

        You will be given some scientific text and either:
        - A LinkML schema (use it directly for extraction)
        - Text only (generate a schema first, then extract)

        You can output as much or as little data as you think is sensible, as long as it is
        supported by the scientific text. 

        The LinkML schema describes the knowledge that the user wants to extract. Pay particular
        attention to entity types and relationships defined in the schema. These describe
        the types of things the user are interested in, and relationships between them.

        The schema may include some advice about what annotators to use when using the 
        ontology search tools to ground the terms to the schema. For example, the following items
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
          
        the "annotators" items can each be passed directly to search_ontology_with_oak() 

        ## 🔬 ONTOLOGY MAPPING STRATEGY:
        
        The schema defines different entity types (classes) and specifies which ontology should be used for grounding each type through the "annotators" field. Pay close attention to these specifications as they indicate the correct ontology for each entity type. When extracting entities from text, identify ALL entity types defined in the schema and ground each entity using a robust two-step approach:

        **STRUCTURED SYSTEMATIC APPROACH**: 
        1. **Extract entities** from the text naturally as you read it and create ExtractedEntity objects with:
           - text: the entity string (e.g., "cleft palate", "22q11.2 deletion syndrome")
           - entity_type: if you can determine it from context (optional)
           - context: surrounding text (optional)
        2. **Use `ground_entities_with_template_annotators(entities_list, template_content)`** to systematically ground all entities
        3. This function returns a GroundingResults object with:
           - successful_matches: List of EntityGroundingMatch objects showing all ontology matches
           - no_matches: Entities that couldn't be grounded
           - annotators_used: Which ontologies were searched
           - summary: Human-readable summary
        4. Use the structured GroundingResults to populate your final output with proper ontology mappings
        
        This ensures maximum grounding success by combining smart routing with direct ontology search. The schema acts as your guide for both what to extract and where to find standardized identifiers for each extracted entity.

        Some other guidelines:
        1. Use the schema to guide your extraction of knowledge from the scientific text.
        2. Ground entities using the two-step approach above - don't give up after just one attempt.
        3. It's okay to have entities that are not grounded, as long as you are sure they
        are actually entities present in the schema.
        4. **FOCUS ON RELATIONSHIPS**: Carefully analyze what is connected in the text:
           - Look for causal relationships (X causes Y, X leads to Y)
           - Look for functional relationships (X encodes Y, X participates in Y)
           - Look for therapeutic relationships (X treats Y, X inhibits Y)
           - Look for genetic relationships (mutations in X increase risk of Y)
           - Extract BOTH entities in any relationship you identify
        5. Extract ALL relevant entities from the text - be comprehensive.
        6. **Track grounding sources**: When grounding entities, always populate the `grounding_source` field:
           - `"sqlite:obo:mondo"` or "ols:mondo" for MONDO disease ontology
           - `"sqlite:obo:hgnc"` for HGNC gene nomenclature
           - `"sqlite:obo:hp"` or "ols:hp" for Human Phenotype Ontology
           - `"sqlite:obo:go"` or "ols:go" for Gene Ontology
           - `"sqlite:chebi"` or "ols:chebi" for chemical entities
           - `"web_search"` for entities grounded via web search
        7. In the "potentially_missing" field, identify important terms that might have been missed:
           - Look for gene names, protein names, drug names that weren't extracted
           - Look for disease subtypes, procedures, biological processes
           - Pay special attention to entities mentioned in relationships
           - Note why each might have been missed (e.g., "not in schema", "complex terminology")
        8. Output structured knowledge in JSON format matching the schema.
        9. Do not respond conversationally, output structured data only.
        """,
        tools=[
            search_ontology_with_oak,
            search_ontology_terms,  # Full ontology mapper agent delegation
            generate_and_validate_schema,  # Schema generator with LinkML validation
            ground_entities_with_template_annotators  # Systematic grounding with template annotators
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
