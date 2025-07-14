"""MONDO disease recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class MondoMetadata(Dict[str, Any]):
    """Metadata dictionary for MONDO evaluations."""
    pass


# MONDO evaluation cases from CRAFT corpus - extracted from real text
huntington_disease = Case(
    name="Huntington disease",
    inputs="In the case of Huntington disease the loss of 15-30% of the normal complement of medium spiny neurons leads to distinct movement disorder in both humans and transgenic mouse models [14-17].",
    expected_output={'ontology_id': "MONDO:0007739"},
    metadata=metadata("easy", "disease_recognition")
)

movement_disorder = Case(
    name="movement disorder",
    inputs="In the case of Huntington disease the loss of 15-30% of the normal complement of medium spiny neurons leads to distinct movement disorder in both humans and transgenic mouse models [14-17].",
    expected_output={'ontology_id': "MONDO:0005395"},
    metadata=metadata("easy", "disease_recognition")
)

x_linked_cleft_palate_and_ankyloglossia = Case(
    name="X-linked cleft palate and ankyloglossia",
    inputs="For example, mutations in Tbx22 cause the human syndrome X-linked cleft palate and ankyloglossia (Braybrook et al.",
    expected_output={'ontology_id': "MONDO:0010560"},
    metadata=metadata("hard", "disease_recognition")
)


def create_mondo_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create MONDO disease recognition evaluation dataset from CRAFT corpus."""
    cases = [
        huntington_disease, movement_disorder, x_linked_cleft_palate_and_ankyloglossia
    ]

    evaluators = [SimpleEntityEvaluator()]

    return Dataset(
        cases=cases,
        evaluators=evaluators
    )
