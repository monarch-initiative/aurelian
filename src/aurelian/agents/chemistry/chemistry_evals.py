"""
Evaluation module for the Chemistry agent.

This module implements evaluations for the Chemistry agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

from aurelian.agents.chemistry.chemistry_agent import chemistry_agent
from aurelian.agents.chemistry.chemistry_config import ChemistryDependencies

class ChemistryMetadata(Dict[str, Any]):
    """Simple metadata dictionary for Chemistry evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="caffeine_structure",
    inputs="Explain the structure of caffeine (CHEBI:27732)",
    expected_output="methylxanthine",  # Should mention methylxanthine structure
    metadata=metadata("medium", "structure_explanation")
)

case2 = Case(
    name="aspirin_properties",
    inputs="What does the structure of aspirin (CHEBI:15365) tell us about its properties?",
    expected_output="acetyl",  # Should mention acetyl group
    metadata=metadata("medium", "structure_property_relationship"),
    evaluators=[
        LLMJudge(
            rubric="Answer should explain how the acetyl group affects aspirin's properties and mention its action as a COX inhibitor",
            include_input=True
        )
    ]
)

case3 = Case(
    name="smiles_interpretation",
    inputs="Interpret this SMILES: CC(=O)OC1=CC=CC=C1C(=O)O",
    expected_output="aspirin",  # This is aspirin
    metadata=metadata("hard", "smiles_interpretation")
)

case4 = Case(
    name="functional_groups",
    inputs="Identify all functional groups in paracetamol (CHEBI:46195)",
    expected_output="amide",  # Should identify the amide group
    metadata=metadata("medium", "functional_group_identification")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the Chemistry agent.
    
    Returns:
        Dataset of Chemistry evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4]
    
    # Dataset-level evaluators
    evaluators = [
        SubstringEvaluator(),
        LLMJudge(
            rubric="Answer should be scientifically accurate and use proper chemistry terminology",
            model="anthropic:claude-3-7-sonnet-latest"
        )
    ]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )