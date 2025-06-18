"""Knowledge Agent for scientific knowledge extraction."""

from typing import Any, Union, Optional
import time
import re
from pathlib import Path

from pydantic_ai import Agent
import logfire

from .knowledge_agent_models import KnowledgeAgentOutput

from aurelian.agents.knowledge_agent.knowledge_agent_config import KnowledgeAgentDependencies
from aurelian.agents.knowledge_agent.knowledge_agent_tools import (
    search_ontology_with_oak
)
from ..web.web_mcp import search_web


# Path to templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_template(template_name: str) -> Optional[str]:
    """Load a template by name.
    
    Args:
        template_name: The name of the template or path to the template
        
    Returns:
        The template content or None if not found
    """
    # If the template_name is a full path, try to load it directly
    template_path = Path(template_name)
    if template_path.exists() and template_path.is_file():
        return template_path.read_text()
    
    # If it's just a name, check if it's in the templates directory
    if not template_name.endswith(".yaml"):
        template_name += ".yaml"
    
    template_path = TEMPLATES_DIR / template_name
    if template_path.exists() and template_path.is_file():
        return template_path.read_text()
    
    # Also try the name without extension
    template_path = TEMPLATES_DIR / template_name.replace(".yaml", "")
    if template_path.exists() and template_path.is_file():
        return template_path.read_text()
    
    return None


def extract_template_name(prompt: str) -> Optional[str]:
    """Extract template name from the prompt if mentioned.
    
    Args:
        prompt: The user prompt
        
    Returns:
        The template name if found, None otherwise
    """
    # Look for patterns like "using the X template" or "with template X"
    patterns = [
        r"using\s+the\s+([a-zA-Z0-9_-]+)(?:\s+template|\s+schema)",
        r"with\s+(?:the\s+)?(?:template|schema)\s+([a-zA-Z0-9_-]+)",
        r"template\s+(?:is|named|called)\s+([a-zA-Z0-9_-]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


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

        You can output as much or as little knowledge as you think is sensible, as long
        as it is supported by the scientific text. 

        When extracting knowledge, pay particular attention to entities and 
        relationships defined in the schema. These describe the types of things the 
        user are interested in, and relationships between them.

        The schema may include `id_prefixes` that will tell you how to ground the 
        entities to the schema. The id_prefixes show which ontology prefixes to use 
        when grounding entities. 
        
        For example, the following items in the schema mean that you should use 
        GO to ground entities of type CellularComponent.
        
              CellularComponent:
                is_a: NamedEntity
                annotations:
                  prompt.examples: >-
                    tubulin complex, proteasome complex, cytoplasm, keratohyalin granule,
                    nucleus
                id_prefixes:
                  - GO
        
        Note that when looking for ontology terms that you can ground entities to, the
        search should take into account synonyms. Also, synonyms may be incomplete, so if
        you cannot find a concept of interest, try searching using related or synonymous
        terms. For example, if you do not find a term for  'eye defect' or 'eye issues' 
        in the Human Phenotype Ontology, try searching for "abnormality of  eye" or 
        "eye abnormality" instead. Also be sure to check for upper and lower case 
        variations of the term.
        
        **Instructions for entity recognition, grounding**: 
        1. **Extract entities** from the text naturally as you read it and create 
        ExtractedEntity objects with:
           - text: the entity string (e.g., "cleft palate", "22q11.2 deletion syndrome")
           - entity_type: if you can determine it from context (optional)
           - context: surrounding text (optional)
        2. **Use `search_ontology_with_oak()`** to try to ground entities. You can try 
        several times with different terms if needed.
        3. This function returns a GroundingResults object with:
           - successful_matches: List of EntityGroundingMatch objects showing all ontology matches
           - no_matches: Entities that couldn't be grounded
           - annotators_used: Which ontologies were searched
           - summary: Human-readable summary
        4. Use the structured GroundingResults to populate your final output with proper 
        ontology mappings
        
        **Instructions for relationship extraction**:
        1. **Extract relationships** between entities as you read the text.
        2. Use the schema to determine the relationship types and their properties.
        3. Create Relationship objects with:
              - subject: the subject entity text
              - predicate: the relationship type (e.g., "biolink:related_to", 
              "biolink:treats", "biolink:interacts_with")
              - object: the object entity text
              - text: the original text supporting the relationship

            
        Some other guidelines:
        1. DO NOT RESPOND CONVERSATIONALLY. Output structured data only.
        2. Use the schema to guide your extraction of knowledge from the scientific text.
        3. Ground entities to ontologies using `search_ontology_with_oak` for precise mapping.
        4. It's okay to have entities that are not grounded, as long as you are sure they
        are actually entities present in the schema.
        5. **FOCUS ON RELATIONSHIPS**: Carefully analyze what is connected in the text. 
        The relationship below are particularly important, but you can use any relationships 
        that are defined in the schema.
        6. **Track grounding sources**: When grounding entities, always populate the 
        `grounding_source` field with the source of the grounding. For example, if you 
        ground a disease to MONDO, set:
              - `grounding_source: "mondo"`
        7. Output structured knowledge in a format matching the schema.
        8. You can use `search_web()` to look up additional information if needed.
        """,
        tools=[
            search_ontology_with_oak,
            search_web
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
        
        # Check if the prompt mentions a template name
        template_name = extract_template_name(prompt)
        if template_name:
            logfire.info(f"Detected template reference: {template_name}")
            template_content = load_template(template_name)
            
            if template_content:
                # Format the prompt with the schema content
                prompt = f"""
                Schema: {template_content}
                
                Text: {prompt}
                
                Extract entities according to the schema.
                """
                logfire.info(f"Loaded template: {template_name}")
            else:
                logfire.warning(f"Failed to load template: {template_name}")

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
