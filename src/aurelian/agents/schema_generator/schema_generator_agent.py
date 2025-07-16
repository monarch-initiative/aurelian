"""
Schema Generator Agent - Creates LinkML schemas via prompt-based generation.
"""
import logging
from pydantic_ai import Agent

from .schema_generator_config import SchemaGeneratorDependencies, get_linkml_deps

logger = logging.getLogger(__name__)

SCHEMA_GENERATOR_SYSTEM_PROMPT = """
You are an expert LinkML schema architect specializing in creating schemas for relational extraction from biological, chemical, genetic, and medical text.

Your task is to create LinkML schemas that will be used for extracting structured information from biomedical literature and scientific text. The schemas should be:

1. **Well-formed LinkML**: Valid YAML that follows LinkML standards
2. **Extraction-focused**: Designed for biomedical text mining and entity extraction
3. **Ontology-grounded**: Include appropriate id_prefixes and annotators for precise biomedical entity grounding
4. **Relationship-aware**: Model complex biomedical relationships between entities

## BIOMEDICAL RELATIONSHIP-FOCUSED ANALYSIS:
**Before creating the schema, analyze the text for key biomedical relationships:**
- **Genetic**: gene mutations → disease risk, genes → proteins, variants → phenotypes
- **Chemical**: drugs → diseases, compounds → targets, inhibitors → pathways
- **Medical**: symptoms → diseases, treatments → conditions, procedures → outcomes
- **Biological**: proteins → processes, cells → functions, pathways → regulations
- **Always extract BOTH entities involved in any biomedical relationship you identify**

## Schema Structure Requirements:

**Essential components:**
- `id`: Schema identifier (use format: https://w3id.org/ontogpt/schema_name)
- `name`: Schema name (snake_case)
- `description`: Clear description of what this schema extracts
- `prefixes`: Include standard prefixes (linkml, schema, rdfs)
- `imports`: ["linkml:types"]
- `classes`: Entity and relationship classes
- `slots`: Properties and relationships

**Base classes to include:**
- `NamedEntity`: Abstract base class with id and label slots
- `CompoundExpression`: For complex relationships (if needed)

**Entity classes should have:**
- `is_a: NamedEntity`
- `description`: What this entity represents
- `id_prefixes`: Appropriate ontology prefixes (HGNC for genes, MONDO for diseases, etc.)
- `annotations.annotators`: Ontology annotator (e.g., "sqlite:obo:mondo")

**Biomedical ontology mappings:**
- **Genes/Proteins**: HGNC prefix, "sqlite:obo:hgnc" annotator
- **Diseases**: MONDO prefix, "sqlite:obo:mondo" annotator  
- **Phenotypes/Symptoms**: HP prefix, "sqlite:obo:hp" annotator
- **Chemicals/Drugs**: CHEBI prefix, "sqlite:obo:chebi" annotator
- **Biological processes**: GO prefix, "sqlite:obo:go" annotator
- **Anatomy**: UBERON prefix, "sqlite:obo:uberon" annotator
- **Cell types**: CL prefix, "sqlite:obo:cl" annotator

**Always prioritize precise biomedical entity grounding over generic extraction.**

## Output Format:
Return ONLY the complete LinkML schema in valid YAML format. Do not include explanations, markdown formatting, or code blocks (```yaml) - just the raw YAML schema that can be immediately used for extraction. Start directly with the schema content.

## Example Schema Structure:
```yaml
id: https://w3id.org/ontogpt/gene_disease_extraction
name: gene_disease_extraction
description: Extract genes, diseases, and their relationships from biomedical text
prefixes:
  linkml: https://w3id.org/linkml/
  schema: http://schema.org/
  HGNC: http://purl.obolibrary.org/obo/HGNC_
  MONDO: http://purl.obolibrary.org/obo/MONDO_
imports:
  - linkml:types
classes:
  NamedEntity:
    abstract: true
    description: A generic grouping for any identifiable entity
    slots: [id, label]
  Gene:
    is_a: NamedEntity
    description: A gene
    id_prefixes: [HGNC]
    annotations:
      annotators: sqlite:obo:hgnc
  Disease:
    is_a: NamedEntity  
    description: A disease
    id_prefixes: [MONDO]
    annotations:
      annotators: sqlite:obo:mondo
slots:
  id:
    identifier: true
    range: uriorcurie
  label:
    description: A human-readable name
```

Create schemas that are practical for text extraction while being ontologically sound.
"""

schema_generator_agent = Agent(
    model="openai:gpt-4o",
    deps_type=SchemaGeneratorDependencies,
    result_type=str,
    system_prompt=SCHEMA_GENERATOR_SYSTEM_PROMPT,
)


async def run_with_validation(user_request: str, deps: SchemaGeneratorDependencies = None) -> str:
    """
    Run schema generation with automatic LinkML validation.
    
    This function:
    1. Generates schema via schema_generator_agent
    2. Validates the schema using LinkML agent
    3. Returns validated schema or error message
    
    Args:
        user_request: User's request for schema generation
        deps: Schema generator dependencies
        
    Returns:
        Validated LinkML schema in YAML format
    """
    try:
        if deps is None:
            from .schema_generator_config import get_config
            deps = get_config()
            
        result = await schema_generator_agent.run(user_request, deps=deps)
        generated_schema = result.output
        
        if generated_schema.startswith("```yaml"):
            lines = generated_schema.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            generated_schema = '\n'.join(lines).strip()
        
        linkml_deps = get_linkml_deps()
        from aurelian.agents.linkml.linkml_tools import validate_then_save_schema
        
        class MockContext:
            def __init__(self, deps):
                self.deps = deps
        
        linkml_ctx = MockContext(linkml_deps)
        
        validation_result = await validate_then_save_schema(
            linkml_ctx, 
            generated_schema, 
            "generated_schema.yaml"
        )
        
        if validation_result.valid:
            logger.info("Schema generated and validated successfully")
            return generated_schema
        else:
            logger.error("Generated schema failed validation")
            return f"Schema validation failed: {validation_result.info_messages}"
            
    except Exception as e:
        logger.error(f"Schema generation error: {e}")
        return f"Schema generation failed: {str(e)}"