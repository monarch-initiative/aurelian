"""UBERON anatomy recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class UberonMetadata(Dict[str, Any]):
    """Metadata dictionary for UBERON evaluations."""
    pass


# UBERON evaluation cases from CRAFT corpus - manually curated
striatum = Case(
    name="striatum",
    inputs="The striatum plays a pivotal role in modulating motor activity and higher cognitive function.",
    expected_output={'ontology_id': "UBERON:0002435"},
    metadata=metadata("easy", "anatomy_recognition")
)

brain = Case(
    name="brain",
    inputs="Brain weight and striatal volume correlate strongly in all strains of mice examined.",
    expected_output={'ontology_id': "UBERON:0000955"},
    metadata=metadata("easy", "anatomy_recognition")
)

central_nervous_system = Case(
    name="central_nervous_system", 
    inputs="From a technical point of view the mouse striatum has several advantages that make it an excellent target for complex trait analysis of the mammalian CNS.",
    expected_output={'ontology_id': "UBERON:0001017"},
    metadata=metadata("medium", "anatomy_recognition")
)

head = Case(
    name="head",
    inputs="The neural crest cells migrate extensively throughout the developing embryo, particularly in the head region.",
    expected_output={'ontology_id': "UBERON:0000033"},
    metadata=metadata("easy", "anatomy_recognition")
)

wing = Case(
    name="wing",
    inputs="During wing development, the expression of signaling molecules is tightly regulated.",
    expected_output={'ontology_id': "UBERON:0000023"},
    metadata=metadata("easy", "anatomy_recognition")
)

pituitary_gland = Case(
    name="pituitary_gland",
    inputs="The pituitary gland secretes hormones that regulate various physiological processes.",
    expected_output={'ontology_id': "UBERON:0000007"},
    metadata=metadata("easy", "anatomy_recognition")
)

peripheral_nervous_system = Case(
    name="peripheral_nervous_system",
    inputs="Neurons of the peripheral nervous system regenerate more readily than those in the central nervous system.",
    expected_output={'ontology_id': "UBERON:0000010"},
    metadata=metadata("medium", "anatomy_recognition")
)

lymph_node = Case(
    name="lymph_node",
    inputs="Immune cells aggregate in the lymph node where they encounter antigens.",
    expected_output={'ontology_id': "UBERON:0000029"},
    metadata=metadata("easy", "anatomy_recognition")
)

tendon = Case(
    name="tendon",
    inputs="The tendon connects muscle to bone and transmits force during movement.",
    expected_output={'ontology_id': "UBERON:0000043"},
    metadata=metadata("easy", "anatomy_recognition")
)

organ = Case(
    name="organ",
    inputs="Each organ has a specific function and is composed of multiple tissue types.",
    expected_output={'ontology_id': "UBERON:0000062"},
    metadata=metadata("easy", "anatomy_recognition")
)


def create_uberon_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create UBERON anatomy recognition evaluation dataset from CRAFT corpus."""
    cases = [
        striatum, brain, central_nervous_system, head, wing, 
        pituitary_gland, peripheral_nervous_system, lymph_node, tendon, organ
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )