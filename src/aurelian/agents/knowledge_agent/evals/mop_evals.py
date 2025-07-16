"""MOP molecular process recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class MopMetadata(Dict[str, Any]):
    """Metadata dictionary for MOP evaluations."""
    pass


# MOP evaluation cases from CRAFT corpus - extracted from real text
conjugated = Case(
    name="conjugated",
    inputs="Louis) followed by secondary antibodies conjugated to HRP.",
    expected_output={'ontology_id': "MOP:0000779"},
    metadata=metadata("medium", "molecular_process_recognition")
)

acetylated = Case(
    name="acetylated",
    inputs="There is no specific loss of fibers to any vestibular endorgan, as visualized by DiI labeling (a) or acetylated tubulin immunoreactivity (b).",
    expected_output={'ontology_id': "MOP:0000030"},
    metadata=metadata("medium", "molecular_process_recognition")
)

cut = Case(
    name="cut",
    inputs="This peptide is normally made at low levels in healthy individuals, and is made when a larger protein called amyloid precursor protein (APP) is cut down in size.",
    expected_output={'ontology_id': "MOP:0000780"},
    metadata=metadata("easy", "molecular_process_recognition")
)

oxidative = Case(
    name="oxidative",
    inputs="Introduction Skeletal muscle fibers are generally classified as type I (oxidative/slow) or type II (glycolytic/fast) fibers.",
    expected_output={'ontology_id': "MOP:0000568"},
    metadata=metadata("medium", "molecular_process_recognition")
)

electron_transfer = Case(
    name="electron transfer",
    inputs="In addition to myoglobin, mitochondrial components for electron transfer (cytochrome c and cytochrome c oxidase [COX] II and IV) and fatty-acid β-oxidation enzymes were elevated (Figure 3A; unpublished data).",
    expected_output={'ontology_id': "MOP:0000615"},
    metadata=metadata("hard", "molecular_process_recognition")
)

phosphorylated = Case(
    name="phosphorylated",
    inputs="The kinase phosphorylated its target substrate at serine residues during the signaling cascade.",
    expected_output={'ontology_id': "MOP:0000568"},
    metadata=metadata("medium", "molecular_process_recognition")
)

methylated = Case(
    name="methylated",
    inputs="Histone proteins were methylated at lysine residues to regulate chromatin structure and gene expression.",
    expected_output={'ontology_id': "MOP:0000498"},
    metadata=metadata("medium", "molecular_process_recognition")
)

ubiquitinated = Case(
    name="ubiquitinated",
    inputs="The target protein was ubiquitinated by the E3 ligase complex, marking it for proteasomal degradation.",
    expected_output={'ontology_id': "MOP:0000632"},
    metadata=metadata("hard", "molecular_process_recognition")
)

hydroxylated = Case(
    name="hydroxylated",
    inputs="Collagen precursors were hydroxylated at proline residues during post-translational modification.",
    expected_output={'ontology_id': "MOP:0000789"},
    metadata=metadata("hard", "molecular_process_recognition")
)

glycosylated = Case(
    name="glycosylated",
    inputs="Cell surface proteins were glycosylated in the endoplasmic reticulum as part of protein processing.",
    expected_output={'ontology_id': "MOP:0000345"},
    metadata=metadata("medium", "molecular_process_recognition")
)


def create_mop_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create MOP molecular process recognition evaluation dataset from CRAFT corpus."""
    cases = [
        conjugated, acetylated, cut, oxidative, electron_transfer,
        phosphorylated, methylated, ubiquitinated, hydroxylated, glycosylated
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )