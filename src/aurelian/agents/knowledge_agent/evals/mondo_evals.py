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

congenital_adrenal_hypoplasia = Case(
    name="congenital adrenal hypoplasia",
    inputs="Consistent with the idea that cells in this primordium are poised between "
           "two developmental pathways, some of the genes that are involved in "
           "establishing sexual dimorphism, including Dax1 (dosage-sensitive sex "
           "reversal-congenital adrenal hypoplasia critical region on the X chromosome "
           "protein 1), Sox9 (Sry-like HMG box 9), Fgf9 (fibroblast growth factor 9), "
           "and Wnt4 (wingless-related MMTV integration site 4), are initially "
           "expressed in similar patterns in XX and XY gonads [3–8].",
    expected_output={'ontology_id': "MONDO:0016241"},
    metadata=metadata("hard", "disease_recognition")
)

severe_acute_respiratory_syndrome = Case(
    name="severe acute respiratory syndrome",
    inputs="Examples of such very successful and useful modeling efforts are provided "
            "by HIV protease [11], or very recently by the peptidase from a "
            "coronavirus involved in the severe acute respiratory syndrome [12], "
            "among others.",
    expected_output={'ontology_id': "MONDO:0005091"},
    metadata=metadata("easy", "disease_recognition")
)

mucolipidosis_type_IV = Case(
    name="mucolipidosis type IV",
    inputs="Mucolipidosis type IV (MLIV) is an autosomal recessive lysosomal storage "
           "disorder characterized by severe neurologic and ophthalmologic "
           "abnormalities.",
    expected_output={'ontology_id': "MONDO:0009653"},
    metadata=metadata("easy", "disease_recognition")
)


def create_mondo_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create MONDO disease recognition evaluation dataset from CRAFT corpus."""
    cases = [
        huntington_disease, movement_disorder, x_linked_cleft_palate_and_ankyloglossia,
        congenital_adrenal_hypoplasia, severe_acute_respiratory_syndrome,
        mucolipidosis_type_IV
    ]

    evaluators = [SimpleEntityEvaluator()]

    return Dataset(
        cases=cases,
        evaluators=evaluators
    )
