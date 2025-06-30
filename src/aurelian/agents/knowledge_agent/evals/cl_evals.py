"""CL cell type recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class ClMetadata(Dict[str, Any]):
    """Metadata dictionary for CL evaluations."""
    pass


# CL evaluation cases from CRAFT corpus - extracted from real text
neuron = Case(
    name="neuron",
    inputs="Neuron-packing density ranged from approximately 50,000 to 100,000 neurons/mm3, and the striatal neuron population ranged from 1.4 to 2.5 million.",
    expected_output={'ontology_id': "CL:0000540"},
    metadata=metadata("easy", "cell_recognition")
)

interneuron = Case(
    name="interneuron",
    inputs="Numbers of medium spiny neurons and ratios of these and less numerous striatal interneurons are critical variables that influence motor performance and aspects of cognition.",
    expected_output={'ontology_id': "CL:0000099"},
    metadata=metadata("medium", "cell_recognition")
)

cell = Case(
    name="cell",
    inputs="In this study we use a forward genetic approach [21, 22] to begin to map and characterize members of the subset of normally polymorphic genes that specifically modulate the production and survival of striatal neurons.",
    expected_output={'ontology_id': "CL:0000000"},
    metadata=metadata("easy", "cell_recognition")
)

granule_cell = Case(
    name="granule cell",
    inputs="The volume of the granule cell layer of the dentate gyrus varies as much as 40-80% among different inbred strains of mice [33-35].",
    expected_output={'ontology_id': "CL:0000120"},
    metadata=metadata("medium", "cell_recognition")
)

pyramidal_cell = Case(
    name="pyramidal cell",
    inputs="More recent experiments using stereologic techniques have reported substantial variation in both neuron number and volume of the pyramidal and dentate cell layers of the hippocampus [36].",
    expected_output={'ontology_id': "CL:0000598"},
    metadata=metadata("medium", "cell_recognition")
)

retinal_ganglion_cell = Case(
    name="retinal ganglion cell",
    inputs="There is also substantial among-strain variation in other structures in the nervous system including the nucleus of the solitary tract [37], the spinal nucleus of the bulbocavernosus [38], and retinal ganglion cells [39, 40].",
    expected_output={'ontology_id': "CL:0000740"},
    metadata=metadata("hard", "cell_recognition")
)

medium_spiny_neuron = Case(
    name="medium spiny neuron",
    inputs="In the case of Huntington disease the loss of 15-30% of the normal complement of medium spiny neurons leads to distinct movement disorder in both humans and transgenic mouse models [14-17].",
    expected_output={'ontology_id': "CL:1001474"},
    metadata=metadata("hard", "cell_recognition")
)

fibroblast = Case(
    name="fibroblast",
    inputs="Pellet of chick embryo fibroblasts expressing RCAS-Shh was prepared by trypsinizing CEF cultures and washing cells in Hanks' Balanced Salt Solution (HBSS).",
    expected_output={'ontology_id': "CL:0000057"},
    metadata=metadata("easy", "cell_recognition")
)

stem_cell = Case(
    name="stem cell",
    inputs="Neural stem cells have the potential to differentiate into multiple cell types during development.",
    expected_output={'ontology_id': "CL:0000034"},
    metadata=metadata("medium", "cell_recognition")
)

germ_cell = Case(
    name="germ cell",
    inputs="The development of germ cells is essential for reproduction in sexually reproducing organisms.",
    expected_output={'ontology_id': "CL:0000586"},
    metadata=metadata("medium", "cell_recognition")
)


def create_cl_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create CL cell type recognition evaluation dataset from CRAFT corpus."""
    cases = [
        neuron, interneuron, cell, granule_cell, pyramidal_cell, 
        retinal_ganglion_cell, medium_spiny_neuron, fibroblast, stem_cell, germ_cell
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )