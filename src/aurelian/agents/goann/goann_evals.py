"""
Evaluation module for the GO Annotation agent.

This module implements evaluations for the GO Annotation agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

from aurelian.agents.goann.goann_agent import goann_agent
from aurelian.agents.goann.goann_config import GOAnnotationDependencies, get_config

class GOAnnotationMetadata(Dict[str, Any]):
    """Simple metadata dictionary for GO Annotation evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="notch1_review",
    inputs="Review GO annotations for human NOTCH1 (P46531)",
    expected_output="transcription",  # Should mention transcription-related functions
    metadata=metadata("medium", "protein_annotation_review")
)

case2 = Case(
    name="tf_coregulator_difference",
    inputs="Explain the difference between DNA-binding transcription factors and coregulators",
    expected_output="bind DNA",  # Should mention DNA binding as key distinction
    metadata=metadata("medium", "concept_explanation"),
    evaluators=[
        LLMJudge(
            rubric="""
            Answer should clearly explain:
            1. DNA-binding TFs directly interact with DNA via specific domains
            2. Coregulators modulate transcription without directly binding DNA
            3. The different functional roles of each in gene expression
            """,
            include_input=True
        )
    ]
)

case3 = Case(
    name="tf_annotation_guidelines",
    inputs="What are the guidelines for annotating transcription factors?",
    expected_output="evidence",  # Should mention evidence requirements
    metadata=metadata("hard", "annotation_guideline_retrieval")
)

case4 = Case(
    name="tf_annotation_check",
    inputs="Check if P46531 is correctly annotated as a DNA-binding transcription factor",
    expected_output="NOTCH",  # Should identify it as NOTCH1
    metadata=metadata("hard", "annotation_accuracy_check")
)

case5 = Case(
    name="pmid_annotation_quality",
    inputs="Find GO annotations from PMID:12345678 and assess their quality",
    expected_output="evidence code",  # Should mention evidence codes in assessment
    metadata=metadata("medium", "literature_annotation_assessment")
)

case6 = Case(
    name="evidence_code_reliability",
    inputs="What evidence codes are most reliable for transcription factor annotations?",
    expected_output="IDA",  # Should mention IDA (Inferred from Direct Assay)
    metadata=metadata("easy", "evidence_code_assessment")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the GO Annotation agent.
    
    Returns:
        Dataset of GO Annotation evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4, case5, case6]
    
    # Dataset-level evaluators
    evaluators = [
        SubstringEvaluator(),
        LLMJudge(
            rubric="""
            Evaluate the answer based on:
            1. Accuracy in explaining GO annotation concepts and guidelines
            2. Proper use of GO terminology and evidence codes
            3. Correct assessment of annotation quality where relevant
            4. Alignment with current GO Consortium best practices
            """,
            model="anthropic:claude-3-7-sonnet-latest"
        )
    ]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )