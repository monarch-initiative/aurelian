"""
Evaluation module for the Diagnosis agent.

This module implements evaluations for the Diagnosis agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset

from aurelian.agents.diagnosis.diagnosis_agent import diagnosis_agent
from aurelian.agents.diagnosis.diagnosis_config import DiagnosisDependencies, get_config

class DiagnosisMetadata(Dict[str, Any]):
    """Simple metadata dictionary for Diagnosis evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="hutchinson_gilford_progeria",
    inputs="""Patient has growth failure, distinct facial features, alopecia, and skin aging.
    Findings excluded: Pigmented nevi, cafe-au-lait spots, and photosensitivity.
    Onset was in infancy.
    Return diagnosis with MONDO ID""",
    expected_output="MONDO:0010135",  # Hutchinson-Gilford Progeria Syndrome
    metadata=metadata("hard", "diagnosis")
)

case2 = Case(
    name="marfan_eye_phenotypes",
    inputs="What eye phenotypes does Marfan syndrome have?",
    expected_output="lens",  # Should mention lens dislocation/ectopia lentis
    metadata=metadata("medium", "phenotype_retrieval")
)

case3 = Case(
    name="eds_type1_id",
    inputs="What is the ID for Ehlers-Danlos syndrome type 1?",
    expected_output="MONDO:0007947",  # EDS classic type 1
    metadata=metadata("easy", "id_retrieval")
)

case4 = Case(
    name="eds_types",
    inputs="What are the kinds of Ehlers-Danlos syndrome?",
    expected_output="hypermobility",  # Should mention hypermobility type
    metadata=metadata("medium", "classification")
)

case5 = Case(
    name="eds_literature_search",
    inputs="Look at phenotypes for Ehlers-Danlos classic type 2. Do a literature search to look at latest studies. What is missing from the KB?",
    expected_output="study",  # Should reference studies
    metadata=metadata("hard", "literature_analysis")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the Diagnosis agent.
    
    Returns:
        Dataset of Diagnosis evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4, case5]
    
    # Dataset-level evaluators
    evaluators = [SubstringEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )