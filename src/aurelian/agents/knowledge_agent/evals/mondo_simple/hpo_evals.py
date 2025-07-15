"""HPO phenotypic feature recognition evaluation cases."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class HpoMetadata(Dict[str, Any]):
    """Metadata dictionary for HPO evaluations."""
    pass


# HPO phenotypic feature test cases
huntington_movement_abnormality = Case(
    name="movement abnormality in Huntington disease",
    inputs="In the case of Huntington disease the loss of 15-30% of the normal complement of medium spiny neurons leads to distinct movement disorder in both humans and transgenic mouse models [14-17].",
    expected_output={'ontology_id': "HP:0100022"},
    metadata=metadata("medium", "phenotype_recognition")
)


def create_hpo_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create HPO phenotypic feature recognition evaluation dataset."""
    cases = [
        huntington_movement_abnormality
    ]

    evaluators = [SimpleEntityEvaluator()]

    return Dataset(
        cases=cases,
        evaluators=evaluators
    )