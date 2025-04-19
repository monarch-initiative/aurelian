"""
Evaluation module for the LinkML agent.

This module implements evaluations for the LinkML agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset

from aurelian.agents.linkml.linkml_agent import linkml_agent
from aurelian.agents.linkml.linkml_config import LinkMLDependencies

class LinkMLMetadata(Dict[str, Any]):
    """Simple metadata dictionary for LinkML evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="schema_generation_food",
    inputs="Generate a schema for modeling the chemical components of foods",
    expected_output="class",  # We expect the output to contain schema classes
    metadata=metadata("medium", "schema_generation")
)

case2 = Case(
    name="schema_from_json",
    inputs="Generate a schema for this data: {name: 'joe', age: 22}",
    expected_output="Person",  # Expected to infer a Person class
    metadata=metadata("easy", "schema_inference")
)

case3 = Case(
    name="schema_validation",
    inputs="Is this a valid LinkML schema? types: string: {base: str}",
    expected_output="valid",  # Checking agent can validate schema snippets
    metadata=metadata("medium", "schema_validation")
)

case4 = Case(
    name="schema_recommendations",
    inputs="What's the best way to model a many-to-many relationship in LinkML?",
    expected_output="multivalued",  # Should mention multivalued attributes
    metadata=metadata("hard", "best_practices")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the LinkML agent.
    
    Returns:
        Dataset of LinkML evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4]
    
    # Dataset-level evaluators
    evaluators = [SubstringEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )