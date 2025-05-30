"""Scientific Knowledge Extraction Agent for extracting structured knowledge from scientific papers.

This agent is focused on extracting knowledge from scientific papers and structuring it
as edges for knowledge graphs, with subjects, predicates, and objects mapped to standard
ontologies and biolink predicates.
"""

import os
from typing import List, Dict, Any, Optional
from pydantic_ai import Agent, Tool

from pydantic_ai.agent import Agent
from pydantic_ai import models

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


def get_scientific_knowledge_extraction_agent():
    return Agent(
        model=models.infer_model("gpt-4"),
        provider="openai",
    )

# Optionally, you can keep a singleton pattern if needed
_scientific_knowledge_extraction_agent = None


def get_scientific_knowledge_extraction_agent():
    global _scientific_knowledge_extraction_agent
    if _scientific_knowledge_extraction_agent is None:
        _scientific_knowledge_extraction_agent = Agent(
            model=models.infer_model("gpt-4"),
            provider="openai",
        )
    return _scientific_knowledge_extraction_agent


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
)

# Register tools with the agent
scientific_knowledge_extraction_agent.tool(list_pdf_files)
scientific_knowledge_extraction_agent.tool(read_pdf)
scientific_knowledge_extraction_agent.tool(extract_knowledge)
scientific_knowledge_extraction_agent.tool(ground_to_ontology)
scientific_knowledge_extraction_agent.tool(map_to_biolink)
scientific_knowledge_extraction_agent.tool(create_kg_edges)
scientific_knowledge_extraction_agent.tool(export_to_kgx)


# CLI helper to process a directory of PDFs
async def process_directory(pdf_dir: str, output_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Process all PDFs in a directory and extract knowledge from them.

    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Optional directory for outputs (defaults to pdf_dir/kg_output)

    Returns:
        List of extracted knowledge edges
    """
    # Create dependencies
    if output_dir is None:
        output_dir = os.path.join(pdf_dir, "kg_output")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize dependencies
    deps = ScientificKnowledgeExtractionDependencies(
        pdf_directory=pdf_dir,
        output_directory=output_dir
    )

    # Create RunContext
    class RunContext:
        def __init__(self, deps):
            self.dependencies = deps

    ctx = RunContext(deps)

    # List PDF files
    pdf_files = await list_pdf_files(ctx)
    print(f"Found {len(pdf_files)} PDF files in {pdf_dir}")

    # Process each PDF file
    all_edges = []

    for pdf_file in pdf_files:
        file_path = pdf_file["file_path"]
        filename = pdf_file["filename"]

        print(f"Processing {filename}...")

        try:
            # Read the PDF
            pdf_data = await read_pdf(ctx, file_path)

            # Extract knowledge
            edges = await extract_knowledge(ctx, pdf_data)
            print(f"  Extracted {len(edges)} knowledge edges")

            # Process each edge through the ontology mapping pipeline
            processed_edges = await create_kg_edges(ctx, edges)
            all_edges.extend(processed_edges)
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

    # Export to KGX format
    if all_edges:
        output_path = os.path.join(output_dir, "knowledge_graph.json")
        result = await export_to_kgx(ctx, all_edges, "knowledge_graph.json")
        print(f"Exported {result.get('node_count', 0)} nodes and {result.get('edge_count', 0)} edges to {result.get('output_path')}")

    return all_edges


# Simple test function to verify the agent imports properly
def test_agent():
    print("Scientific Knowledge Extraction Agent imported successfully")
    return scientific_knowledge_extraction_agent

# If this file is run directly, execute the test function
if __name__ == "__main__":
    test_agent()
