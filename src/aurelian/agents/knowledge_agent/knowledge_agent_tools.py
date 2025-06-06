"""Tools for the Knowledge Agent."""

import os
from typing import List, Tuple, Optional

from oaklib import get_adapter
from pydantic_ai import RunContext


async def search_ontology_with_oak(term: str, ontology: str, n: int = 10, verbose: bool = False) -> List[Tuple[str, str]]:
    """
    Search an OBO ontology for a term.

    Note that search should take into account synonyms, but synonyms may be incomplete,
    so if you cannot find a concept of interest, try searching using related or synonymous
    terms.

    If you are searching for a composite term, try searching on the sub-terms to get a sense
    of the terminology used in the ontology.

    Args:
        term: The term to search for.
        ontology: The ontology ID to search
        n: The maximum number of results to return.
        verbose: Whether to print debug information.

    Returns:
        A list of tuples, each containing an ontology ID and a label.
    """
    adapter = get_adapter("ols:" + ontology)
    results = adapter.basic_search(term)
    if n:
        results = list(results)[:n]
    labels = list(adapter.labels(results))
    if verbose:
        print(f"## TOOL USE: Searched for '{term}' in '{ontology}' ontology")
        print(f"## RESULTS: {labels}")
    return labels


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
