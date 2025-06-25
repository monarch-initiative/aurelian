"""Evaluation cases for Knowledge Agent."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class KnowledgeAgentMetadata(Dict[str, Any]):
    """Simple metadata dictionary for Knowledge Agent evaluations."""
    pass




# Define a simple test case for Marfan Syndrome with mondo_simple template
marfan_case = Case(
    name="marfan_mondo_simple",
    inputs="Marfan Syndrome is characterized by heart defects",
    expected_output={'ontology_id': "MONDO:0007947"},
    metadata=metadata("easy", "disease_recognition")
)


def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create a dataset for evaluating the Knowledge Agent."""

    # Collect all cases
    cases = [marfan_case]

    # Simple substring evaluator - just checks if the expected text is in the output
    evaluators = [SimpleEntityEvaluator()]

    return Dataset(
        cases=cases,
        evaluators=evaluators
    )
