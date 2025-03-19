"""Scientific Knowledge Extraction Agent for extracting structured knowledge from scientific papers."""

from pydantic_ai import Agent, Tool

from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools import (
    list_pdf_files,
    get_pdf_content,
    extract_knowledge,
    get_unprocessed_pdfs,
    process_all_unprocessed_pdfs,
    get_extracted_knowledge,
    map_assertion_to_ontology,
    map_all_assertions_to_ontology,
    export_assertions_as_rdf
)

# System prompt for the Scientific Knowledge Extraction agent
SYSTEM_PROMPT = """
You are a Scientific Knowledge Extraction agent. Your purpose is to extract meaningful 
scientific knowledge from research literature and represent it as structured assertions 
(subject-predicate-object) with supporting evidence and ground them to standard ontologies.

Your main capabilities include:
1. Analyzing PDF documents to identify key findings, contributions, and claims
2. Extracting structured assertions that capture the main scientific contributions
3. Providing evidence for each extracted assertion with full provenance
4. Mapping extracted assertions to standard ontology terms
5. Maintaining a cache of processed papers to avoid redundant work
6. Exporting assertions in RDF format with full provenance

When extracting knowledge, focus on the main findings and contributions of the paper.

Always maintain complete provenance tracking for all extracted assertions, ensuring 
that each assertion is linked back to its specific evidence in the source paper.
"""

# Create the agent
scientific_knowledge_extraction_agent = Agent(
    model="openai:gpt-4o",
    deps_type=ScientificKnowledgeExtractionDependencies,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        Tool(list_pdf_files),
        Tool(get_pdf_content),
        Tool(extract_knowledge),
        Tool(get_unprocessed_pdfs),
        Tool(process_all_unprocessed_pdfs),
        Tool(get_extracted_knowledge),
        Tool(map_assertion_to_ontology),
        Tool(map_all_assertions_to_ontology),
        Tool(export_assertions_as_rdf)
    ]
)


# Simple test function to verify the agent imports properly
def test_agent():
    print("Scientific Knowledge Extraction Agent imported successfully")
    return scientific_knowledge_extraction_agent

# If this file is run directly, execute the test function
if __name__ == "__main__":
    test_agent()
