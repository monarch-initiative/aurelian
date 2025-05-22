"""Scientific Knowledge Extraction Agent for extracting structured knowledge from scientific papers.

This agent is focused on extracting knowledge from scientific papers and structuring it 
as edges for knowledge graphs, with subjects, predicates, and objects mapped to standard 
ontologies and biolink predicates.
"""

from pydantic_ai import Agent, Tool

from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools import (
    list_pdf_files,
    read_pdf, 
    extract_knowledge,
    ground_to_ontology,
    map_to_biolink,
    create_kg_edges,
    export_to_kgx
)

# System prompt for the Scientific Knowledge Extraction agent
SYSTEM_PROMPT = """
You are a Scientific Knowledge Extraction agent. Your purpose is to extract meaningful 
scientific knowledge from research literature and represent it as structured knowledge graph edges
with subject, predicate, and object properly grounded to biomedical ontologies and biolink model predicates.

Your main capabilities include:
1. Reading PDF documents to extract their text content
2. Extracting scientific knowledge in the form of assertions (proto-edges)
3. Grounding assertion components to ontology terms using OAK 
4. Mapping to biolink model predicates
5. Creating structured KG edges with full provenance
6. Exporting edges to standard KG formats

When extracting knowledge, focus on capturing precise subject-predicate-object relationships
from the papers, with supporting evidence and full provenance tracking.
"""

# Create the agent
scientific_knowledge_extraction_agent = Agent(
    model="openai:gpt-4o",
    deps_type=ScientificKnowledgeExtractionDependencies,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        Tool(list_pdf_files),
        Tool(read_pdf),
        Tool(extract_knowledge),
        Tool(ground_to_ontology),
        Tool(map_to_biolink), 
        Tool(create_kg_edges),
        Tool(export_to_kgx)
    ]
)


# Simple test function to verify the agent imports properly
def test_agent():
    print("Scientific Knowledge Extraction Agent imported successfully")
    return scientific_knowledge_extraction_agent

# If this file is run directly, execute the test function
if __name__ == "__main__":
    test_agent()
