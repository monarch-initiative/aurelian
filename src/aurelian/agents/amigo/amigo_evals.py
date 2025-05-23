"""
Evaluation module for the AmiGO agent.

This module implements evaluations for the AmiGO agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset

from aurelian.agents.amigo.amigo_agent import amigo_agent
from aurelian.agents.amigo.amigo_config import AmiGODependencies

class AmiGOMetadata(Dict[str, Any]):
    """Simple metadata dictionary for AmiGO evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="uniprot_annotations",
    inputs="What are some annotations for the protein UniProtKB:Q9UMS5",
    expected_output="GO:",  # Should contain GO terms
    metadata=metadata("medium", "annotation_retrieval")
)

case2 = Case(
    name="paper_overannotation",
    inputs="Check PMID:19661248 for over-annotation",
    expected_output="annotation",  # Should evaluate the paper's annotations
    metadata=metadata("hard", "literature_assessment")
)

case3 = Case(
    name="pathway_genes",
    inputs="What genes are involved in the ribosome biogenesis pathway?",
    expected_output="ribosom",  # Should mention ribosome-related genes
    metadata=metadata("medium", "pathway_analysis")
)

case4 = Case(
    name="database_mapping",
    inputs="Map UniProtKB:P04637 to KEGG database",
    expected_output="KEGG",  # Should contain KEGG IDs
    metadata=metadata("easy", "database_mapping")
)

case5 = Case(
    name="dna_repair_genes",
    inputs="Search for genes involved in DNA repair and show me their annotations",
    expected_output="repair",  # Should mention DNA repair annotations
    metadata=metadata("medium", "gene_function_search")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the AmiGO agent.
    
    Returns:
        Dataset of AmiGO evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4, case5]
    
    # Dataset-level evaluators
    evaluators = [SubstringEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )