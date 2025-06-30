"""NCBITaxon organism recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class NcbitaxonMetadata(Dict[str, Any]):
    """Metadata dictionary for NCBITaxon evaluations."""
    pass


# NCBITaxon evaluation cases from CRAFT corpus - extracted from real text
mice = Case(
    name="mice",
    inputs="Brn3c null mutant mice show long-term, incomplete retention of some afferent inner ear innervation Abstract Background Ears of Brn3c null mutants develop immature hair cells, identifiable only by certain molecular markers, and undergo apoptosis in neonates.",
    expected_output={'ontology_id': "NCBITaxon:10088"},
    metadata=metadata("easy", "organism_recognition")
)

mammals = Case(
    name="mammals",
    inputs="In the ear [4] as well as elsewhere [10] neurotrophins are progressively downregulated in postnatal mammals and possibly replaced by other factors [11].",
    expected_output={'ontology_id': "NCBITaxon:40674"},
    metadata=metadata("medium", "organism_recognition")
)

animals = Case(
    name="animals",
    inputs="We want to evaluate a possible correlation between the topology of sensory neuron loss and absence of a specific neurotrophin or topological loss of hair cells at birth and in older animals.",
    expected_output={'ontology_id': "NCBITaxon:33208"},
    metadata=metadata("easy", "organism_recognition")
)

human = Case(
    name="human",
    inputs="This information could be important for an in-depth evaluation of the human deafness related to the Pou4f3 gene, DFNA15 [12].",
    expected_output={'ontology_id': "NCBITaxon:9606"},
    metadata=metadata("easy", "organism_recognition")
)

rodents = Case(
    name="rodents",
    inputs="This retention of apical spiral neurons is also largely unrelated to neurotrophins which are known to be reduced in their expression in neonatal rodents [4].",
    expected_output={'ontology_id': "NCBITaxon:9989"},
    metadata=metadata("medium", "organism_recognition")
)

cat = Case(
    name="cat",
    inputs="Comparable long term retention of apical spiral sensory neurons was described for the deaf white cat [25] and may also be the case in humans with congenital deafness.",
    expected_output={'ontology_id': "NCBITaxon:9685"},
    metadata=metadata("easy", "organism_recognition")
)

organisms = Case(
    name="organisms",
    inputs="Structure-function evolution of the Transforming acidic coiled coil genes revealed by analysis of phylogenetically diverse organisms Abstract Background Examination of ancient gene families can provide an insight into how the evolution of gene structure can relate to function.",
    expected_output={'ontology_id': "NCBITaxon:1"},
    metadata=metadata("hard", "organism_recognition")
)

C_elegans = Case(
    name="C elegans",
    inputs="We have also extended the analysis of the TACCs to the interaction databases of C. elegans and D.",
    expected_output={'ontology_id': "NCBITaxon:6239"},
    metadata=metadata("medium", "organism_recognition")
)

D_melanogaster = Case(
    name="D melanogaster",
    inputs="elegans and D. melanogaster to identify potentially novel TACC interactions.",
    expected_output={'ontology_id': "NCBITaxon:7227"},
    metadata=metadata("medium", "organism_recognition")
)

Xenopus_laevis = Case(
    name="Xenopus laevis",
    inputs="To date, only three active TACC genes have been cloned in humans [1-3], one in each of mouse [7], Xenopus laevis [8], D.",
    expected_output={'ontology_id': "NCBITaxon:8355"},
    metadata=metadata("hard", "organism_recognition")
)


def create_ncbitaxon_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create NCBITaxon organism recognition evaluation dataset from CRAFT corpus."""
    cases = [
        mice, mammals, animals, human, rodents,
        cat, organisms, C_elegans, D_melanogaster, Xenopus_laevis
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )