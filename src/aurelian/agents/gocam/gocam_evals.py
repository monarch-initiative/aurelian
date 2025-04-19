"""
Evaluation module for the GO-CAM agent.

This module implements evaluations for the GO-CAM agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset

from aurelian.agents.gocam.gocam_agent import gocam_agent
from aurelian.agents.gocam.gocam_config import GOCAMDependencies

class GOCAMMetadata(Dict[str, Any]):
    """Simple metadata dictionary for GO-CAM evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="apoptosis_genes",
    inputs="Find a model relating to apoptosis and list their genes",
    expected_output="CASP",
    metadata=metadata("medium", "information_retrieval")
)

case2 = Case(
    name="count_gene_products",
    inputs="How many distinct gene products in 62b4ffe300001804? Answer with a number, e.g. 7.",
    expected_output="4",
    metadata=metadata("easy", "counting")
)

case3 = Case(
    name="nonexistent_model",
    inputs="Find a model with ID gomodel:1234 and summarize it",
    expected_output=None,  # Just checking the agent doesn't error out
    metadata=metadata("medium", "error_handling")
)

case4 = Case(
    name="signaling_receptor_id",
    inputs="When curating GO-CAMs, the activity unit for a ligand of a signaling receptor should use which GO MF ID for the activity unit?",
    expected_output="0048018",
    metadata=metadata("hard", "knowledge_retrieval")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the GO-CAM agent.
    
    Returns:
        Dataset of GO-CAM evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4]
    
    # Dataset-level evaluators
    evaluators = [SubstringEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )

