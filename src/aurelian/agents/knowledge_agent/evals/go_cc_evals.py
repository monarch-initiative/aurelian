"""GO_CC cellular component recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class GoCcMetadata(Dict[str, Any]):
    """Metadata dictionary for GO_CC evaluations."""
    pass


# GO_CC evaluation cases from CRAFT corpus - extracted from real text
cell_projection = Case(
    name="cell projection",
    inputs="Approximately 90% of all neurons in the striatum - 1.5 to 2.5 million in mice [1,2] and 110-200 million in humans [3,4] - belong to an unusual type of inhibitory projection cell referred to as medium spiny neurons [5-8].",
    expected_output={'ontology_id': "GO:0042995"},
    metadata=metadata("medium", "cellular_component_recognition")
)

nucleolus = Case(
    name="nucleolus",
    inputs="The nucleolus is a prominent subnuclear structure involved in ribosome biogenesis.",
    expected_output={'ontology_id': "GO:0005730"},
    metadata=metadata("medium", "cellular_component_recognition")
)

axon = Case(
    name="axon",
    inputs="In addition, Vax1 interacts with several molecules including sonic hedgehog,Pax2, Pax6, and Rx that are known to be important during development of the basal forebrain [27, 50].",
    expected_output={'ontology_id': "GO:0030424"},
    metadata=metadata("medium", "cellular_component_recognition")
)

x_chromosome = Case(
    name="X chromosome",
    inputs="For example, mutations in Tbx22 cause the human syndrome X-linked cleft palate and ankyloglossia (Braybrook et al.",
    expected_output={'ontology_id': "GO:0000805"},
    metadata=metadata("easy", "cellular_component_recognition")
)

autosome = Case(
    name="autosome",
    inputs="The deH phenotype exhibits little overlap with these features; instead, we suggest a more likely candidate for mutations of human TBX15 would be frontofacionasal syndrome, an unmapped autosomal recessive condition characterized by brachycephaly, blepharophimosis, and midface hypoplasia (Reardon et al.",
    expected_output={'ontology_id': "GO:0030849"},
    metadata=metadata("medium", "cellular_component_recognition")
)

synapse = Case(
    name="synapse",
    inputs="Striatal neurons are divided into two major subpopulations (patch and matrix), that have somewhat different gene expression profiles and have different patterns of pre- and postsynaptic connections [9-13].",
    expected_output={'ontology_id': "GO:0045202"},
    metadata=metadata("medium", "cellular_component_recognition")
)

postsynapse = Case(
    name="postsynapse",
    inputs="Striatal neurons are divided into two major subpopulations (patch and matrix), that have somewhat different gene expression profiles and have different patterns of pre- and postsynaptic connections [9-13].",
    expected_output={'ontology_id': "GO:0098794"},
    metadata=metadata("hard", "cellular_component_recognition")
)

presynapse = Case(
    name="presynapse",
    inputs="Striatal neurons are divided into two major subpopulations (patch and matrix), that have somewhat different gene expression profiles and have different patterns of pre- and postsynaptic connections [9-13].",
    expected_output={'ontology_id': "GO:0098793"},
    metadata=metadata("hard", "cellular_component_recognition")
)

y_chromosome = Case(
    name="Y chromosome",
    inputs="Sex chromosomes including the Y chromosome carry genes important for sex determination.",
    expected_output={'ontology_id': "GO:0000806"},
    metadata=metadata("easy", "cellular_component_recognition")
)

nucleus = Case(
    name="nucleus",
    inputs="The dorsal striatum is a massive nucleus in the basal forebrain that plays a pivotal role in modulating motor activity and higher cognitive function.",
    expected_output={'ontology_id': "GO:0005634"},
    metadata=metadata("easy", "cellular_component_recognition")
)


def create_go_cc_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create GO_CC cellular component recognition evaluation dataset from CRAFT corpus."""
    cases = [
        cell_projection, nucleolus, axon, x_chromosome, autosome,
        synapse, postsynapse, presynapse, y_chromosome, nucleus
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )