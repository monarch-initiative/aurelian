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

opitz_syndrome = Case(
    name="Opitz G/BBB syndrome",
    inputs="Opitz G/BBB syndrome is a genetic disorder characterized by developmental midline abnormalities, such as hypertelorism, cleft palate, and hypospadias.",
    expected_output={'ontology_id': "MONDO:0017138"},
    metadata=metadata("medium", "disease_recognition")
)

prostate_cancer = Case(
    name="prostate cancer",
    inputs="Complete inactivation of the PTEN tumor suppressor gene is extremely common in advanced cancer, including prostate cancer (CaP).",
    expected_output={'ontology_id': "MONDO:0008315"},
    metadata=metadata("easy", "disease_recognition")
)

fragile_x_syndrome = Case(
    name="fragile X syndrome", 
    inputs="For example, expression defects in the KH domain proteins NOVA and FMRP are known to cause paraneoplastic neurologic disorders and the fragile X syndrome, respectively, in humans.",
    expected_output={'ontology_id': "MONDO:0010383"},
    metadata=metadata("medium", "disease_recognition")
)

nephrogenic_diabetes_insipidus = Case(
    name="nephrogenic diabetes insipidus",
    inputs="Congenital nephrogenic diabetes insipidus (NDI) is a disease characterized by failure of the kidney to concentrate urine in response to vasopressin.",
    expected_output={'ontology_id': "MONDO:0016383"},
    metadata=metadata("hard", "disease_recognition")
)

breast_cancer = Case(
    name="breast cancer",
    inputs="BRCA2 was the second breast cancer susceptibility gene to be discovered, and was isolated through positional cloning using data from families with inherited breast cancer.",
    expected_output={'ontology_id': "MONDO:0007254"},
    metadata=metadata("easy", "disease_recognition")
)

late_infantile_neuronal_ceroid_lipofuscinosis = Case(
    name="late-infantile neuronal ceroid lipofuscinosis",
    inputs="In humans, defects in expression of this enzyme lead to a fatal neurodegenerative disease, classical late-infantile neuronal ceroid lipofuscinosis.",
    expected_output={'ontology_id': "MONDO:0015674"},
    metadata=metadata("hard", "disease_recognition")
)

acute_erythroid_leukemia = Case(
    name="erythroleukemia",
    inputs="Transgenic studies in zebrafish and other model organisms have provided insights into the molecular mechanisms underlying various blood cancers including erythroleukemia.",
    expected_output={'ontology_id': "MONDO:0017858"},
    metadata=metadata("medium", "disease_recognition")
)

spinocerebellar_ataxia_15 = Case(
    name="Spinocerebellar Ataxia 15",
    inputs="We observed a severe autosomal recessive movement disorder in mice used within our laboratory and found it underlies Spinocerebellar Ataxia 15 in humans.",
    expected_output={'ontology_id': "MONDO:0011694"},
    metadata=metadata("hard", "disease_recognition")
)

peliosis_hepatis = Case(
    name="peliosis hepatis",
    inputs="Liver pathologies that closely resemble the human syndrome known as peliosis hepatis that has been described in association with Bartonella henselae infection, long-term high-dose androgen therapy, or rarely with advanced cancers.",
    expected_output={'ontology_id': "MONDO:0004717"},
    metadata=metadata("hard", "disease_recognition")
)

cerebellar_ataxia = Case(
    name="ataxia",
    inputs="Neurotrophin-3 acts as a chemoattractant for sensory axons and its deficiency can lead to movement disorders including ataxia.",
    expected_output={'ontology_id': "MONDO:0000437"},
    metadata=metadata("medium", "disease_recognition")
)

cystic_fibrosis = Case(
    name="cystic fibrosis",
    inputs="Cystic fibrosis is a genetic disorder that affects primarily the lungs and digestive system, caused by mutations in the CFTR gene.",
    expected_output={'ontology_id': "MONDO:0009061"},
    metadata=metadata("easy", "disease_recognition")
)

duchenne_muscular_dystrophy = Case(
    name="Duchenne muscular dystrophy",
    inputs="Duchenne muscular dystrophy is a severe form of muscular dystrophy caused by mutations in the dystrophin gene, leading to progressive muscle degeneration.",
    expected_output={'ontology_id': "MONDO:0010679"},
    metadata=metadata("medium", "disease_recognition")
)

retinoblastoma = Case(
    name="retinoblastoma",
    inputs="Retinoblastoma is the most common primary intraocular malignancy in children, arising from the neural retina and caused by mutations in the RB1 gene.",
    expected_output={'ontology_id': "MONDO:0008380"},
    metadata=metadata("medium", "disease_recognition")
)


def create_mondo_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create MONDO disease recognition evaluation dataset from CRAFT corpus."""
    cases = [
        huntington_disease, movement_disorder, x_linked_cleft_palate_and_ankyloglossia,
        congenital_adrenal_hypoplasia, severe_acute_respiratory_syndrome,
        mucolipidosis_type_IV, opitz_syndrome, prostate_cancer, fragile_x_syndrome,
        nephrogenic_diabetes_insipidus, breast_cancer, late_infantile_neuronal_ceroid_lipofuscinosis,
        acute_erythroid_leukemia, spinocerebellar_ataxia_15, peliosis_hepatis, cerebellar_ataxia,
        cystic_fibrosis, duchenne_muscular_dystrophy, retinoblastoma
    ]

    evaluators = [SimpleEntityEvaluator()]

    return Dataset(
        cases=cases,
        evaluators=evaluators
    )
