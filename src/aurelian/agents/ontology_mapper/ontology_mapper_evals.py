"""
Evaluation module for the Ontology Mapper agent.

This module implements evaluations for the Ontology Mapper agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

from aurelian.agents.ontology_mapper.ontology_mapper_agent import ontology_mapper_agent
from aurelian.agents.ontology_mapper.ontology_mapper_config import OntologyMapperDependencies, get_config

class OntologyMapperMetadata(Dict[str, Any]):
    """Simple metadata dictionary for Ontology Mapper evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="cell_ontology_neuron",
    inputs="Find the term in the cell ontology for neuron",
    expected_output="CL:0000540",  # Neuron ID in Cell Ontology
    metadata=metadata("easy", "basic_term_lookup")
)

case2 = Case(
    name="middle_fingers_terms",
    inputs="Best terms to use for the middle 3 fingers",
    expected_output="digit",  # Should mention digit terms
    metadata=metadata("medium", "anatomical_term_suggestion"),
    evaluators=[
        LLMJudge(
            rubric="""
            Answer should:
            1. Identify appropriate anatomical terms for index, middle, and ring fingers
            2. Include ontology IDs where possible
            3. Explain why these terms are appropriate
            """,
            include_input=True
        )
    ]
)

case3 = Case(
    name="go_cell_division",
    inputs="What is the term for the process of cell division in GO?",
    expected_output="GO:0051301",  # Cell division GO term
    metadata=metadata("easy", "go_term_lookup")
)

case4 = Case(
    name="mp_term_mapping",
    inputs="""
    Find good MP terms for the following. If no matches can be found, suggest appropriate action

    * CA1 TBS Reduced
    * CA1 TBS Increased
    * Surface righting Reduced
    * Contextual fear conditioning (shock context/context shock) Reduced
    * Morris water maze Reduced
    * Rotarod Increased
    * Rotarod Reduced
    """,
    expected_output="MP:",  # Should provide MP IDs
    metadata=metadata("hard", "complex_term_mapping")
)

case5 = Case(
    name="cross_ontology_mapping",
    inputs="Map the Human Phenotype Ontology term for 'Seizure' (HP:0001250) to Mouse Phenotype Ontology",
    expected_output="MP:0002064",  # Seizure in MP
    metadata=metadata("medium", "cross_ontology_mapping")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the Ontology Mapper agent.
    
    Returns:
        Dataset of Ontology Mapper evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4, case5]
    
    # Dataset-level evaluators
    evaluators = [
        SubstringEvaluator(),
        LLMJudge(
            rubric="""
            Evaluate the answer based on:
            1. Accuracy of ontology term identification
            2. Correctness of ontology IDs provided
            3. Appropriateness of term selection for the given context
            4. Clear explanation of term selection logic and relationships
            5. Suitable handling of cases where no exact match exists
            """,
            model="anthropic:claude-3-7-sonnet-latest"
        )
    ]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )