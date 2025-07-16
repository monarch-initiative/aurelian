"""Tools for the Knowledge Agent."""

import os
import urllib

import yaml
from typing import List, Tuple, Optional, Dict, Any

from oaklib import get_adapter
from pydantic_ai import RunContext
from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    """A single entity extracted from text."""
    text: str = Field(description="The entity text as found in the source")
    entity_type: Optional[str] = Field(None, description="The type of entity if known (e.g., 'gene', 'disease', 'phenotype')")
    context: Optional[str] = Field(None, description="Surrounding context from the original text")


class EntityGroundingMatch(BaseModel):
    """A grounding match for an entity in a specific ontology."""
    entity: str = Field(description="The original entity text")
    entity_type: str = Field(description="The entity class from the template (e.g., 'DiseaseTerm', 'PhenotypeTerm')")
    ontology_id: str = Field(description="The ontology identifier (e.g., 'MONDO:0018923')")
    ontology_label: str = Field(description="The ontology term label")
    annotator: str = Field(description="The annotator used (e.g., 'sqlite:obo:mondo')")
    confidence: str = Field(description="Confidence level: 'high', 'medium', 'low'")


class GroundingResults(BaseModel):
    """Comprehensive grounding results for all entities."""
    entities_processed: List[str] = Field(description="List of entity texts that were processed")
    annotators_used: Dict[str, str] = Field(description="Mapping of entity class to annotator string")
    successful_matches: List[EntityGroundingMatch] = Field(description="All successful ontology matches")
    no_matches: List[str] = Field(description="Entities that could not be grounded")
    summary: str = Field(description="Human-readable summary of the grounding results")


async def search_ontology_with_oak(term: str, ontology: str, n: int = 10, verbose: bool = True) -> List[Tuple[str, str]]:
    """
    Search an OBO ontology for a term.

    Note that search should take into account synonyms, but synonyms may be incomplete,
    so if you cannot find a concept of interest, try searching using related or synonymous
    terms. For example, if you do not find a term for 'eye defect' in the Human Phenotype Ontology,
    try searching for "abnormality of eye" and also try searching for "eye" and then
    looking through the results to find the more specific term you are interested in.

    Also remember to check for upper and lower case variations of the term.

    If you are searching for a composite term, try searching on the sub-terms to get a sense
    of the terminology used in the ontology.

    Args:
        term: The term to search for.
        ontology: The ontology ID to search. You can try prepending "ols:" to an ontology
        name to use the ontology lookup service (OLS), for example "ols:mondo" or
        "ols:hp". Try first using "ols:". You can also try prepending "sqlite:obo:" to
        an ontology name to use the local sqlite version of ontologies, but
        **you should prefer "ols:" because it seems to do better for finding
        non-exact matches!**

        Recommended ontologies for common biomedical concepts:
            - "ols:mondo" — diseases from the MONDO disease ontology
            - "sqlite:obo:hgnc" — human gene symbols from HGNC
            - "ols:hp" — phenotypic features from the Human Phenotype Ontology
            - "ols:go" — molecular functions, biological processes, and cellular
            components from the Gene Ontology
            - "ols:chebi" — chemical entities from the ChEBI ontology
            - "ols:uberon" — anatomical structures from the Uberon ontology
            - "ols:cl" — cell types from the Cell Ontology
            - "ols:so" — sequence features from the Sequence Ontology
            - "ols:pr" — protein entities from the Protein Ontology (PRO)
            - "ols:ncit" — terms related to clinical research from the NCI Thesaurus
            - "ols:snomed" - SNOMED CT terms for clinical concepts. This includes
            LOINC, if you need to search for clinical measurements/tests
        n: The maximum number of results to return.
        verbose: Whether to print debug information.

    Returns:
        A list of tuples, each containing an ontology ID and a label.
    """
    # try / except
    try:
        adapter = get_adapter(ontology)
        results = adapter.basic_search(term)
        results = list(adapter.labels(results))
    except (ValueError, urllib.error.URLError, KeyError) as e:
        print(f"## TOOL WARNING: Unable to search ontology '{ontology}' - unknown url type: '{ontology}'")
        return None
    if n:
        results = list(results)[:n]

    if verbose:
        print(f"## TOOL USE: Searched for '{term}' in '{ontology}' ontology")
        print(f"## RESULTS: {results}")
    return results


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text from the PDF
    """
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF extraction. Install it with `poetry install -E pdf`")

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"

    return text


def process_pdf_files(pdf_paths: List[str], max_pages: Optional[int] = None,
                      page_limit_per_file: Optional[int] = None) -> str:
    """
    Process multiple PDF files and extract their text.

    Args:
        pdf_paths: List of paths to PDF files
        max_pages: Maximum total number of pages to process across all files
        page_limit_per_file: Maximum number of pages to process per file

    Returns:
        Extracted text from all PDFs, concatenated
    """
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF extraction. Install it with `poetry install -E pdf`")

    all_text = ""
    total_pages_processed = 0

    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            print(f"Warning: PDF file not found: {pdf_path}")
            continue

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            # Apply per-file page limit if specified
            if page_limit_per_file:
                pages_to_process = min(num_pages, page_limit_per_file)
            else:
                pages_to_process = num_pages

            # Check if we've hit the maximum total pages
            if max_pages and total_pages_processed + pages_to_process > max_pages:
                pages_to_process = max_pages - total_pages_processed

            if pages_to_process <= 0:
                break

            # Extract text from pages
            file_text = ""
            for page_num in range(pages_to_process):
                page = pdf_reader.pages[page_num]
                file_text += page.extract_text() + "\n\n"

            # Add filename as header
            file_basename = os.path.basename(pdf_path)
            all_text += f"\n\n--- PDF: {file_basename} ---\n\n{file_text}"

            total_pages_processed += pages_to_process

            # Check if we've hit the maximum total pages
            if max_pages and total_pages_processed >= max_pages:
                break

    return all_text.strip()


def parse_template_annotators(template_content: str) -> Dict[str, str]:
    """
    Parse a LinkML template to extract entity classes and their annotators.

    Args:
        template_content: YAML content of the LinkML template

    Returns:
        Dict mapping entity class names to their annotator strings
    """
    try:
        schema = yaml.safe_load(template_content)
        annotators = {}

        if 'classes' in schema:
            for class_name, class_def in schema['classes'].items():
                if 'annotations' in class_def and 'annotators' in class_def['annotations']:
                    annotator = class_def['annotations']['annotators']
                    annotators[class_name] = annotator
                    print(f"Found {class_name} -> {annotator}")

        return annotators
    except Exception as e:
        print(f"Error parsing template: {e}")
        return {}


async def ground_entities_with_template_annotators(ctx: RunContext, entities: List[ExtractedEntity], template_content: str) -> GroundingResults:
    """
    Ground a list of entities using all annotators from the template.

    This function systematically:
    1. Parses template to get all annotators (e.g., sqlite:obo:mondo, sqlite:obo:hp)
    2. For each entity, searches in ALL annotators
    3. Returns structured GroundingResults showing which entities match in which ontologies

    Args:
        ctx: The run context
        entities: List of ExtractedEntity objects from the LLM
        template_content: YAML content of the LinkML template

    Returns:
        GroundingResults: Structured grounding results for all entities across all template annotators
    """
    # Step 1: Parse template to get all annotators
    annotators = parse_template_annotators(template_content)

    if not annotators:
        return GroundingResults(
            entities_processed=[],
            annotators_used={},
            successful_matches=[],
            no_matches=[],
            summary="No annotators found in template. Cannot proceed with grounding."
        )

    entity_texts = [e.text for e in entities]
    print(f"Template annotators: {annotators}")
    print(f"Entities to ground: {entity_texts}")

    # Step 2: Initialize results
    successful_matches = []
    no_matches = []

    # Step 3: For each entity, search in ALL annotators
    for entity_obj in entities:
        entity_text = entity_obj.text
        print(f"\n--- Grounding '{entity_text}' ---")
        entity_has_matches = False

        for entity_class, annotator in annotators.items():
            try:
                print(f"  Searching in {entity_class} ({annotator})")
                search_results = await search_ontology_with_oak(entity_text, annotator, n=13, verbose=False)

                if search_results:
                    # Take the best match
                    term_id, label = search_results[0]

                    # Determine confidence
                    confidence = "high" if entity_text.lower() in label.lower() else "medium"

                    match = EntityGroundingMatch(
                        entity=entity_text,
                        entity_type=entity_class,
                        ontology_id=term_id,
                        ontology_label=label,
                        annotator=annotator,
                        confidence=confidence
                    )
                    successful_matches.append(match)
                    entity_has_matches = True
                    print(f"    ✓ {term_id} - {label}")
                else:
                    print(f"    ✗ No match")

            except Exception as e:
                print(f"    ✗ Error: {e}")
                continue

        if not entity_has_matches:
            no_matches.append(entity_text)

    # Step 4: Create summary
    summary_lines = [
        f"GROUNDING RESULTS:",
        f"Entities processed: {len(entity_texts)}",
        f"Annotators used: {list(annotators.keys())}",
        ""
    ]

    if successful_matches:
        summary_lines.append(f"SUCCESSFUL MATCHES ({len(successful_matches)}):")
        for match in successful_matches:
            summary_lines.append(f"- '{match.entity}' -> {match.entity_type}: {match.ontology_id} ({match.ontology_label})")

    if no_matches:
        summary_lines.append(f"\nNO MATCHES FOUND:")
        for entity in no_matches:
            summary_lines.append(f"- '{entity}'")

    summary = "\n".join(summary_lines)

    return GroundingResults(
        entities_processed=entity_texts,
        annotators_used=annotators,
        successful_matches=successful_matches,
        no_matches=no_matches,
        summary=summary
    )


async def search_ontology_terms(ctx: RunContext, ontology_id: str, query: str) -> str:
    """
    Intelligent ontology search with smart routing and fallback.

    This function uses AI-powered preprocessing to route queries to appropriate
    ontologies, but can also do direct searches when an ontology is specified.

    Args:
        ctx: The run context
        ontology_id: Ontology preference (e.g., 'mondo', 'hp', 'go') - can be ignored for smart routing
        query: Search query/term

    Returns:
        Detailed ontology search results with smart routing information
    """
    try:
        from aurelian.agents.ontology_mapper.ontology_mapper_agent import ontology_mapper_agent
        ontology_deps = ctx.deps.ontology_mapper if hasattr(ctx.deps, 'ontology_mapper') else ctx.deps

        # SMART ROUTING: Use preprocessing to find the best ontologies
        result = await ontology_mapper_agent.run(
            f"Use smart preprocessing to find the best ontology terms for: '{query}'. "
            f"Use search_with_preprocessing to intelligently route this query to appropriate ontologies. "
            f"If you find good matches, prioritize those. If not, you can also try searching in {ontology_id} as a fallback.",
            usage=ctx.usage if hasattr(ctx, 'usage') else None,
            deps=ontology_deps
        )

        return result.output
    except ImportError:
        return f"Smart ontology search not available. Basic result for '{query}'"


async def generate_and_validate_schema(ctx: RunContext, user_request: str) -> str:
    """
    Generate and validate a LinkML schema for extraction.

    This function:
    1. Calls schema_generator_agent to create the schema
    2. Automatically validates it with LinkML agent
    3. Returns a validated schema ready for extraction

    Use this when:
    - User asks "generate a schema for..."
    - User provides text but no schema for extraction
    - User wants to create schemas for specific domains

    Args:
        ctx: The run context with KnowledgeAgentDependencies
        user_request: The user's request for schema generation

    Returns:
        Generated and validated LinkML schema in YAML format
    """
    try:
        from aurelian.agents.schema_generator.schema_agent import schema_generator_agent
        schema_deps = ctx.deps.schema_generator if hasattr(ctx.deps, 'schema_generator') else None

        if schema_deps is None:
            return "Schema generator dependencies not available in RunContext."

        result = await schema_generator_agent.run(user_request, deps=schema_deps)
        generated_schema = result.output

        # TODO: Add LinkML validation here if needed
        return generated_schema

    except ImportError:
        return "Schema generator not available. Please provide a LinkML schema for extraction."
    except Exception as e:
        return f"Schema generation failed: {str(e)}"
