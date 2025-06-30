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

syndrome = Case(
    name="syndrome",
    inputs="For example, mutations in Tbx22 cause the human syndrome X-linked cleft palate and ankyloglossia (Braybrook et al.",
    expected_output={'ontology_id': "MONDO:0002254"},
    metadata=metadata("easy", "disease_recognition")
)

x_linked_cleft_palate_and_ankyloglossia = Case(
    name="X-linked cleft palate and ankyloglossia",
    inputs="For example, mutations in Tbx22 cause the human syndrome X-linked cleft palate and ankyloglossia (Braybrook et al.",
    expected_output={'ontology_id': "MONDO:0017938"},
    metadata=metadata("hard", "disease_recognition")
)

infectious_disease = Case(
    name="infectious disease",
    inputs="Shh/RCAS-infection of chick wings blocks early muscle differentiation.",
    expected_output={'ontology_id': "MONDO:0005550"},
    metadata=metadata("easy", "disease_recognition")
)

cancer = Case(
    name="cancer",
    inputs="Soriano, Fred Hutchinson Cancer Research Center, Seattle, Washington, United States), and C57BL/6J (B6) ae/ae mice (kindly provided by L.",
    expected_output={'ontology_id': "MONDO:0004992"},
    metadata=metadata("easy", "disease_recognition")
)

hypertrichosis = Case(
    name="hypertrichosis",
    inputs="Originally described as a rare autosomal-dominant syndrome with progressive facial coarsening, overgrowth of the intraoral mucosa, and large, doughy hands, more recent case reports describe macrosomia, macrocephaly, or both and generalized hypertrichosis with progressive coarsening (Dallapiccola et al.",
    expected_output={'ontology_id': "MONDO:0019280"},
    metadata=metadata("hard", "disease_recognition")
)

blepharophimosis = Case(
    name="blepharophimosis",
    inputs="The deH phenotype exhibits little overlap with these features; instead, we suggest a more likely candidate for mutations of human TBX15 would be frontofacionasal syndrome, an unmapped autosomal recessive condition characterized by brachycephaly, blepharophimosis, and midface hypoplasia (Reardon et al.",
    expected_output={'ontology_id': "MONDO:0001008"},
    metadata=metadata("hard", "disease_recognition")
)

neoplasm = Case(
    name="neoplasm",
    inputs="Cytoplasmic galectin-3 correlates with tumor progression and protects mitochondrial integrity.",
    expected_output={'ontology_id': "MONDO:0005070"},
    metadata=metadata("medium", "disease_recognition")
)

disease = Case(
    name="disease",
    inputs="Red blood cells which lack the ability to vesiculate cause a disease with red blood cell destruction and haemoglobinuria [21].",
    expected_output={'ontology_id': "MONDO:0000001"},
    metadata=metadata("easy", "disease_recognition")
)


def create_mondo_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create MONDO disease recognition evaluation dataset from CRAFT corpus."""
    cases = [
        huntington_disease, movement_disorder, syndrome, x_linked_cleft_palate_and_ankyloglossia, 
        infectious_disease, cancer, hypertrichosis, blepharophimosis, neoplasm, disease
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )