"""Tools for the Scientific Knowledge Extraction Agent.

This module provides tools for extracting structured knowledge from scientific papers
and formatting it as edges for knowledge graphs.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
import re
from dataclasses import dataclass
import datetime

from pydantic_ai import RunContext, ModelRetry

# Import utilities from aurelian
from aurelian.utils.pdf_fetcher import extract_text_from_pdf

# We'll use biolink-model package for predicate mapping
try:
    from biolink_model import get_toolkit
    BIOLINK_TOOLKIT = get_toolkit()
    HAVE_BIOLINK_MODEL = True
except ImportError:
    HAVE_BIOLINK_MODEL = False
    print("Warning: biolink-model package not found. Predicate mapping will be limited.")

# Define a basic KG edge structure
@dataclass
class KnowledgeEdge:
    """Represents a knowledge graph edge extracted from scientific literature."""
    
    # Core triple components
    subject: str
    predicate: str
    object: str
    
    # Provenance
    source_id: Optional[str] = None  # DOI or other identifier
    source_title: Optional[str] = None
    evidence_text: Optional[str] = None
    
    # Ontology mapping
    subject_curie: Optional[str] = None
    predicate_curie: Optional[str] = None
    object_curie: Optional[str] = None
    
    # Metadata
    confidence: float = 0.0
    extraction_method: str = "scientific_knowledge_extraction"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary for serialization."""
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "subject_curie": self.subject_curie,
            "predicate_curie": self.predicate_curie,
            "object_curie": self.object_curie,
            "source_id": self.source_id,
            "source_title": self.source_title,
            "evidence_text": self.evidence_text,
            "confidence": self.confidence,
            "extraction_method": self.extraction_method
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEdge':
        """Create edge from dictionary."""
        return cls(**data)


async def list_pdf_files(ctx: RunContext) -> List[Dict[str, Any]]:
    """
    List all PDF files in the configured directory.
    
    Returns:
        A list of dictionaries with PDF file information.
    """
    deps = ctx.dependencies
    
    if not os.path.exists(deps.pdf_directory):
        raise ModelRetry(f"PDF directory '{deps.pdf_directory}' does not exist")
    
    pdf_files = []
    for filename in os.listdir(deps.pdf_directory):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(deps.pdf_directory, filename)
            pdf_files.append({
                "filename": filename,
                "file_path": file_path
            })
    
    return pdf_files


async def read_pdf(ctx: RunContext, file_path: str) -> Dict[str, Any]:
    """
    Read a PDF file and extract its text content.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary with the extracted text and metadata
    """
    try:
        if not os.path.exists(file_path):
            raise ModelRetry(f"PDF file '{file_path}' does not exist")
        
        # Extract text using aurelian's utility
        pdf_text = await extract_text_from_pdf(file_path)
        
        # Try to extract basic metadata from the text
        doi = _extract_doi_from_text(pdf_text)
        title = _extract_title_from_text(pdf_text)
        
        return {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "text": pdf_text,
            "metadata": {
                "doi": doi,
                "title": title
            }
        }
    except Exception as e:
        raise ModelRetry(f"Error reading PDF: {str(e)}")


def _extract_doi_from_text(text: str) -> Optional[str]:
    """Extract DOI from text if present."""
    # Common DOI patterns
    doi_patterns = [
        r'(?:doi|DOI):\s*([0-9]+\.[0-9]+\/[^\s\]\)]+)',
        r'(?:https?://)?(?:dx\.)?doi\.org/([0-9]+\.[0-9]+\/[^\s\]\)]+)'
    ]
    
    for pattern in doi_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


def _extract_title_from_text(text: str) -> Optional[str]:
    """Extract title from PDF text (simple heuristic approach)."""
    # Simple heuristic: first non-empty line that's not a header/journal name
    lines = text.split('\n')
    for line in lines[:20]:  # Check first 20 lines
        line = line.strip()
        if len(line) > 20 and not any(x in line.lower() for x in ['journal', 'doi', 'issn', 'vol']):
            return line
    
    return None


async def extract_knowledge(ctx: RunContext, pdf_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract knowledge from PDF text in the form of subject-predicate-object assertions.
    
    Args:
        pdf_data: Dictionary containing PDF text and metadata from read_pdf
        
    Returns:
        List of extracted knowledge edges
    """
    text = pdf_data.get("text", "")
    metadata = pdf_data.get("metadata", {})
    
    if not text:
        raise ModelRetry("No text found in PDF data")
    
    # For now, we'll implement a placeholder using LLM to extract knowledge
    # This would be replaced with more sophisticated extraction methods
    
    # Split text into manageable chunks (e.g., ~1000 words per chunk)
    text_chunks = _split_text_into_chunks(text, chunk_size=1000)
    
    all_edges = []
    
    # Process each chunk to extract knowledge
    for chunk in text_chunks:
        # Here we'd implement knowledge extraction using LLM
        # For now, we'll return placeholder data
        edges = await _extract_knowledge_from_chunk(ctx, chunk, metadata)
        all_edges.extend(edges)
    
    return [edge.to_dict() for edge in all_edges]


def _split_text_into_chunks(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of approximately chunk_size words."""
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]


async def _extract_knowledge_from_chunk(
    ctx: RunContext, 
    text_chunk: str, 
    metadata: Dict[str, Any]
) -> List[KnowledgeEdge]:
    """Extract knowledge edges from a chunk of text."""
    # This is a placeholder that would be replaced with actual LLM-based extraction
    # In a real implementation, we would:
    # 1. Use an LLM to identify subject-predicate-object triples in the text
    # 2. Format them as KnowledgeEdge objects
    
    # For demo purposes, we'll create a dummy edge if certain keywords are found
    edges = []
    
    if "alzheimer" in text_chunk.lower() or "amyloid" in text_chunk.lower():
        # Create a simple edge about Alzheimer's disease
        edge = KnowledgeEdge(
            subject="Amyloid beta",
            predicate="associated_with",
            object="Alzheimer's disease",
            source_id=metadata.get("doi"),
            source_title=metadata.get("title"),
            evidence_text=text_chunk[:200] + "...",  # First 200 chars as evidence
            confidence=0.8
        )
        edges.append(edge)
    
    return edges


async def ground_to_ontology(ctx: RunContext, edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ground entities in a knowledge edge to ontology terms using OAK.
    
    Args:
        edge: Dictionary representation of a KnowledgeEdge
        
    Returns:
        Updated edge with ontology mappings
    """
    # This is a placeholder for ontology grounding
    # In a real implementation, we would:
    # 1. Use Ontology Access Kit (OAK) to look up terms
    # 2. Find best matches for the subject and object
    
    # For demo purposes, we'll add dummy CURIEs for common terms
    edge_copy = edge.copy()
    
    subject = edge_copy.get("subject", "").lower()
    object_term = edge_copy.get("object", "").lower()
    
    # Add some sample mappings
    if "amyloid" in subject:
        edge_copy["subject_curie"] = "CHEBI:64645"  # Amyloid beta
    elif "tau" in subject:
        edge_copy["subject_curie"] = "PR:000017618"  # Tau protein
    
    if "alzheimer" in object_term:
        edge_copy["object_curie"] = "MONDO:0004975"  # Alzheimer's disease
    
    return edge_copy


async def map_to_biolink(ctx: RunContext, edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map predicates to Biolink Model terms.
    
    Args:
        edge: Dictionary representation of a KnowledgeEdge
        
    Returns:
        Updated edge with Biolink predicate mapping
    """
    edge_copy = edge.copy()
    predicate = edge_copy.get("predicate", "").lower()
    
    # Use biolink-model package if available
    if HAVE_BIOLINK_MODEL:
        # This would use the actual biolink model toolkit to find the best match
        # For now, we'll use a simple mapping
        
        if "associated" in predicate:
            edge_copy["predicate_curie"] = "biolink:associated_with"
        elif "increases" in predicate or "activates" in predicate:
            edge_copy["predicate_curie"] = "biolink:increases_amount_or_activity_of"
        elif "decreases" in predicate or "inhibits" in predicate:
            edge_copy["predicate_curie"] = "biolink:decreases_amount_or_activity_of"
        elif "causes" in predicate:
            edge_copy["predicate_curie"] = "biolink:causes"
        elif "treats" in predicate:
            edge_copy["predicate_curie"] = "biolink:treats"
    else:
        # Simple fallback mapping
        if "associated" in predicate:
            edge_copy["predicate_curie"] = "biolink:associated_with"
        elif "increases" in predicate:
            edge_copy["predicate_curie"] = "biolink:increases_amount_or_activity_of"
    
    return edge_copy


async def create_kg_edges(
    ctx: RunContext, 
    extracted_knowledge: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Create knowledge graph edges from extracted knowledge assertions.
    
    Args:
        extracted_knowledge: List of knowledge assertions
        
    Returns:
        List of knowledge graph edges with ontology mappings
    """
    kg_edges = []
    
    for assertion in extracted_knowledge:
        # Ground entities to ontologies
        grounded_assertion = await ground_to_ontology(ctx, assertion)
        
        # Map predicates to Biolink model
        mapped_assertion = await map_to_biolink(ctx, grounded_assertion)
        
        kg_edges.append(mapped_assertion)
    
    return kg_edges


async def export_to_kgx(
    ctx: RunContext, 
    edges: List[Dict[str, Any]], 
    output_filename: str = "kg_export.json"
) -> Dict[str, Any]:
    """
    Export knowledge graph edges to KGX format.
    
    Args:
        edges: List of knowledge graph edges
        output_filename: Name of output file
        
    Returns:
        Dictionary with export information
    """
    deps = ctx.dependencies
    
    # Format data for KGX JSON format
    nodes = {}
    edge_list = []
    
    # Extract nodes from edges
    for edge in edges:
        # Subject node
        subject_id = edge.get("subject_curie") or f"TEMP:{edge['subject'].replace(' ', '_')}"
        nodes[subject_id] = {
            "id": subject_id,
            "name": edge["subject"],
            "category": ["biolink:NamedThing"]
        }
        
        # Object node
        object_id = edge.get("object_curie") or f"TEMP:{edge['object'].replace(' ', '_')}"
        nodes[object_id] = {
            "id": object_id,
            "name": edge["object"],
            "category": ["biolink:NamedThing"]
        }
        
        # Format edge
        edge_dict = {
            "id": f"edge_{len(edge_list)}",
            "subject": subject_id,
            "predicate": edge.get("predicate_curie", "biolink:related_to"),
            "object": object_id,
            "relation": edge["predicate"],
            "provided_by": "scientific_knowledge_extraction",
            "confidence": edge.get("confidence", 0.0)
        }
        
        # Add provenance if available
        if edge.get("source_id"):
            edge_dict["publication"] = edge["source_id"]
        
        if edge.get("evidence_text"):
            edge_dict["has_evidence"] = edge["evidence_text"]
        
        edge_list.append(edge_dict)
    
    # Prepare output path
    output_path = os.path.join(deps.output_directory, output_filename)
    
    # Write to file
    kgx_data = {
        "nodes": list(nodes.values()),
        "edges": edge_list
    }
    
    with open(output_path, 'w') as f:
        json.dump(kgx_data, f, indent=2)
    
    return {
        "status": "success",
        "output_path": output_path,
        "node_count": len(nodes),
        "edge_count": len(edge_list)
    }