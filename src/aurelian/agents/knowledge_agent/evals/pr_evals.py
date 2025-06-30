"""PR protein recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class PrMetadata(Dict[str, Any]):
    """Metadata dictionary for PR evaluations."""
    pass


# PR evaluation cases from CRAFT corpus - extracted from real text
tubulin = Case(
    name="tubulin",
    inputs="There is no specific loss of fibers to any vestibular endorgan, as visualized by DiI labeling (a) or acetylated tubulin immunoreactivity (b).",
    expected_output={'ontology_id': "PR:000009450"},
    metadata=metadata("easy", "protein_recognition")
)

myosin_VI = Case(
    name="myosin VI",
    inputs="Close examination has revealed that some 'immature' hair cells form in Brn3c null mutants and express cellular markers such as Myosin VI and VIIa, calretinin and parvalbumin [3].",
    expected_output={'ontology_id': "PR:000010868"},
    metadata=metadata("medium", "protein_recognition")
)

Brn3c = Case(
    name="Brn3c",
    inputs="Brn3c null mutant mice show long-term, incomplete retention of some afferent inner ear innervation Abstract Background Ears of Brn3c null mutants develop immature hair cells, identifiable only by certain molecular markers, and undergo apoptosis in neonates.",
    expected_output={'ontology_id': "PR:000013043"},
    metadata=metadata("medium", "protein_recognition")
)

neurotrophin = Case(
    name="neurotrophin",
    inputs="This partial development of hair cells could lead to enough neurotrophin expression to sustain sensory neurons through embryonic development.",
    expected_output={'ontology_id': "PR:000011137"},
    metadata=metadata("medium", "protein_recognition")
)

BDNF = Case(
    name="BDNF",
    inputs="Results At birth there is a limited expression of BDNF and NT-3 in the mutant sensory epithelia and DiI tracing shows no specific reduction of afferents or efferents that resembles neurotrophin null mutations.",
    expected_output={'ontology_id': "PR:000004716"},
    metadata=metadata("easy", "protein_recognition")
)

NT_3 = Case(
    name="NT-3",
    inputs="Results At birth there is a limited expression of BDNF and NT-3 in the mutant sensory epithelia and DiI tracing shows no specific reduction of afferents or efferents that resembles neurotrophin null mutations.",
    expected_output={'ontology_id': "PR:000011459"},
    metadata=metadata("easy", "protein_recognition")
)

myosin_VIIa = Case(
    name="myosin VIIa",
    inputs="1% of myosin VIIa-positive immature hair cells are present in the mutant cochlea, concentrated in the base.",
    expected_output={'ontology_id': "PR:000010869"},
    metadata=metadata("medium", "protein_recognition")
)

calretinin = Case(
    name="calretinin",
    inputs="Close examination has revealed that some 'immature' hair cells form in Brn3c null mutants and express cellular markers such as Myosin VI and VIIa, calretinin and parvalbumin [3].",
    expected_output={'ontology_id': "PR:000004968"},
    metadata=metadata("medium", "protein_recognition")
)

TrkB = Case(
    name="TrkB",
    inputs="Null mutants of BDNF or its receptor trkB lose all innervation to the semicircular canals and have a reduced innervation to the utricle, saccule and apical turn of the cochlea.",
    expected_output={'ontology_id': "PR:000016029"},
    metadata=metadata("hard", "protein_recognition")
)

TrkC = Case(
    name="TrkC",
    inputs="In contrast, null mutations of either NT-3 or its receptor trkC result in loss of spiral neurons in the basal turn with formation of an inner spiral bundle of afferents extending to the basal tip.",
    expected_output={'ontology_id': "PR:000016030"},
    metadata=metadata("hard", "protein_recognition")
)


def create_pr_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create PR protein recognition evaluation dataset from CRAFT corpus."""
    cases = [
        tubulin, myosin_VI, Brn3c, neurotrophin, BDNF, 
        NT_3, myosin_VIIa, calretinin, TrkB, TrkC
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )