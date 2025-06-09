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
        retries=3,
        output_retries=3,
        deps_type=KnowledgeAgentDependencies,
        result_type=KnowledgeAgentOutput,
        system_prompt="""
        You are an expert curator of scientific knowledge. Your purpose is to take 
        unstructured scientific text and output structured scientific knowledge that is 
        aligned to a LinkML schema that describes the knowledge the user wants to extract.

        You can output as much or as little data as you think is sensible, as long as it is
        supported by the scientific text. 

        When extracting knowledge, pay particular attention to entity types and 
        relationships defined in the schema. These describe the types of things the 
        user are interested in, and relationships between them.

        The schema may include some advice about what ontologies to use when using the 
        ontology search tools to ground the terms to the schema. For example, the following items
        in the schema mean that you should use the Mondo Disease Ontology to ground disease 
        terms:

            id_prefixes:
              - MONDO
            annotations:
              annotators: sqlite:obo:mondo
    
        and the following means that you should use the Human Phenotype Ontology:: 
    
            id_prefixes:
            - HP
            annotations:
              annotators: sqlite:obo:hp
          
        the "annotators" items are suggestions about how to ground entities. These 
        typically can each be passed directly to the ontology argument in 
        search_ontology_with_oak(). 
        
        Note that when looking for ontology terms that you can ground entities to, the
        search should take into account synonyms. Also, synonyms may be incomplete, so if
        you cannot find a concept of interest, try searching using related or synonymous
        terms. For example, if you do not find a term for  'eye defect' or 'eye issues' 
        in the Human Phenotype Ontology, try searching for "abnormality of  eye" or 
        "eye abnormality" instead. Also be sure to check for upper and lower case 
        variations of the term.
        
        **STRUCTURED SYSTEMATIC APPROACH**: 
        1. **Extract entities** from the text naturally as you read it and create 
        ExtractedEntity objects with:
           - text: the entity string (e.g., "cleft palate", "22q11.2 deletion syndrome")
           - entity_type: if you can determine it from context (optional)
           - context: surrounding text (optional)
        2. **Use `ground_entities_with_template_annotators(entities_list, template_content)`** 
        to systematically ground all entities
        3. This function returns a GroundingResults object with:
           - successful_matches: List of EntityGroundingMatch objects showing all ontology matches
           - no_matches: Entities that couldn't be grounded
           - annotators_used: Which ontologies were searched
           - summary: Human-readable summary
        4. Use the structured GroundingResults to populate your final output with proper 
        ontology mappings
        
        This ensures maximum grounding success by combining smart routing with direct 
        ontology search. The schema acts as your guide for both what to extract and 
        where to find standardized identifiers for each extracted entity.

        Some other guidelines:
        1. DO NOT RESPOND CONVERSATIONALLY. Output structured data only.
        2. Use the schema to guide your extraction of knowledge from the scientific text.
        3. Ground entities to ontologies using `search_ontology_terms` for precise mapping.
        4. It's okay to have entities that are not grounded, as long as you are sure they
        are actually entities present in the schema.
        5. **FOCUS ON RELATIONSHIPS**: Carefully analyze what is connected in the text. 
        The relationship below are particularly important, but you can use any relationships 
        that are defined in the schema. Here are some common relationships you can use:
           
            biolink:has_phenotype
            Description: Captures observable traits linked to diseases or genetic disorders.
            Example: "Disease X has_phenotype fever."

            biolink:gene_encodes_gene_product
            Description: Connects a gene to the protein or RNA product it encodes.
            Example: "The BRCA1 gene encodes the BRCA1 protein."

            biolink:physically_interacts_with
            Description: Indicates that two gene products bind or directly interact with each other.
            Example: "Protein A physically interacts with Protein B."

            biolink:causes
            Description: Describes a direct causal link between an entity (e.g., variant, exposure) and a disease or phenotype.
            Example: "Mutation in Gene X causes Disease Y."

            biolink:positively_regulates
            Description: Indicates that one entity increases the activity or expression of another.
            Example: "Transcription factor X positively regulates Gene Y."

            biolink:negatively_regulates
            Description: Indicates that one entity decreases or represses the activity or expression of another.
            Example: "miRNA Z negatively regulates Target A expression."
            
            biolink:associated_with
            Description: Denotes a non-causal but statistically or biologically meaningful association between two entities.
            Example: "Gene A is associated with Disease B."
            
            biolink:affects
            Description: Indicates that one entity alters or influences another, without specifying the direction or mechanism.
            Example: "Drug X affects blood pressure."
            
            biolink:treats
            Description: Connects a treatment (e.g., drug, therapy) to a disease or condition it ameliorates.
            Example: "Drug D treats Hypertension."
            
            biolink:inhibits
            Description: Specifies that one entity suppresses the function, expression, or activity of another.
            Example: "Compound X inhibits Enzyme Y."
            
            biolink:participates_in
            Description: Links a molecular entity or process to a broader biological process or pathway.
            Example: "Protein P participates in the apoptosis pathway."
            
            biolink:subclass_of
            Description: Indicates a hierarchical relationship where one class is a more specific instance of another.
            Example: "MicroRNA is a subclass_of GeneProduct."
            
            biolink:has_variant
            Description: Connects a gene to a specific sequence variant.
            Example: "Gene X has_variant X123Y."
            
            biolink:has_publication
            Description: Associates an assertion or relationship with a supporting publication or citation.
            Example: "This association has_publication PMID:123456."
            
            biolink:related_to
            Description: A generic relationship used when the specific nature of the connection is unknown or broad.
            Example: "Symptom A is related_to Disease B."
            
        6. **Track grounding sources**: When grounding entities, always populate the 
        `grounding_source` field with the source of the grounding. For example, if you 
        ground a disease to MONDO, set:
              - `grounding_source: "mondo"`
        7. Output structured knowledge in a format matching the schema.
        """,
        tools=[
            search_ontology_with_oak,
            # generate_and_validate_schema,  # Schema generator with LinkML validation
            # search_ontology_terms,  # Full ontology mapper agent delegation
            # ground_entities_with_template_annotators  # Systematic grounding with template annotators
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
