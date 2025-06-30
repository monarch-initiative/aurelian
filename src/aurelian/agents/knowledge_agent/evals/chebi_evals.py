"""CHEBI chemical recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class ChebiMetadata(Dict[str, Any]):
    """Metadata dictionary for CHEBI evaluations."""
    pass


# CHEBI evaluation cases from CRAFT corpus - extracted from real text
water = Case(
    name="water",
    inputs="Mice were anesthetized deeply with Avertin (1.25% 2,2,2-tribromoethanol and 0.8% tert-pentyl alcohol in water, 0.5-1.0 ml ip) and perfused through the left ventricle with 0.9% sodium phosphate buffered (PB) saline (pH 7.4) followed by 1.25% glutaraldehyde/1.0% paraformaldehyde in 0.1 M PB (pH 7.40) over a period of 2 to 4 min.",
    expected_output={'ontology_id': "CHEBI:15377"},
    metadata=metadata("easy", "chemical_recognition")
)

glutaraldehyde = Case(
    name="glutaraldehyde",
    inputs="Mice were anesthetized deeply with Avertin (1.25% 2,2,2-tribromoethanol and 0.8% tert-pentyl alcohol in water, 0.5-1.0 ml ip) and perfused through the left ventricle with 0.9% sodium phosphate buffered (PB) saline (pH 7.4) followed by 1.25% glutaraldehyde/1.0% paraformaldehyde in 0.1 M PB (pH 7.40) over a period of 2 to 4 min.",
    expected_output={'ontology_id': "CHEBI:5478"},
    metadata=metadata("medium", "chemical_recognition")
)

sodium_phosphate = Case(
    name="sodium phosphate",
    inputs="Mice were anesthetized deeply with Avertin (1.25% 2,2,2-tribromoethanol and 0.8% tert-pentyl alcohol in water, 0.5-1.0 ml ip) and perfused through the left ventricle with 0.9% sodium phosphate buffered (PB) saline (pH 7.4) followed by 1.25% glutaraldehyde/1.0% paraformaldehyde in 0.1 M PB (pH 7.40) over a period of 2 to 4 min.",
    expected_output={'ontology_id': "CHEBI:37586"},
    metadata=metadata("medium", "chemical_recognition")
)

paraformaldehyde = Case(
    name="paraformaldehyde",
    inputs="Mice were anesthetized deeply with Avertin (1.25% 2,2,2-tribromoethanol and 0.8% tert-pentyl alcohol in water, 0.5-1.0 ml ip) and perfused through the left ventricle with 0.9% sodium phosphate buffered (PB) saline (pH 7.4) followed by 1.25% glutaraldehyde/1.0% paraformaldehyde in 0.1 M PB (pH 7.40) over a period of 2 to 4 min.",
    expected_output={'ontology_id': "CHEBI:16842"},
    metadata=metadata("medium", "chemical_recognition")
)

cholinergic = Case(
    name="cholinergic",
    inputs="The number of striatal cholinergic neurons, for example, varies 50% among 26 BXD RI lines [32].",
    expected_output={'ontology_id': "CHEBI:38462"},
    metadata=metadata("hard", "chemical_recognition")
)

formalin = Case(
    name="formalin",
    inputs="An additional 10-ml of double-strength fixative (2.5% glutaraldehyde/2.0% paraformaldehyde) was injected for 1 to 2 min at an increased flow rate followed by overnight post-fixation in the same medium in 4°C, after which the brains were removed, soaked in 30% sucrose for 48 h, frozen in powdered dry ice, and cut into 30-μm sections in the transverse plane using a sliding microtome [40]. Sections were mounted onto gelatin-coated slides and air-dried overnight at room temperature and then processed for in situ hybridization as described elsewhere [1, 42], or post-fixed in formalin, dehydrated in a graded alcohol series, and embedded in paraffin.",
    expected_output={'ontology_id': "CHEBI:16842"},
    metadata=metadata("medium", "chemical_recognition")
)

sucrose = Case(
    name="sucrose",
    inputs="An additional 10-ml of double-strength fixative (2.5% glutaraldehyde/2.0% paraformaldehyde) was injected for 1 to 2 min at an increased flow rate followed by overnight post-fixation in the same medium in 4°C, after which the brains were removed, soaked in 30% sucrose for 48 h, frozen in powdered dry ice, and cut into 30-μm sections in the transverse plane using a sliding microtome [40].",
    expected_output={'ontology_id': "CHEBI:17992"},
    metadata=metadata("easy", "chemical_recognition")
)

alcohol = Case(
    name="alcohol",
    inputs="Sections were mounted onto gelatin-coated slides and air-dried overnight at room temperature and then processed for in situ hybridization as described elsewhere [1, 42], or post-fixed in formalin, dehydrated in a graded alcohol series, and embedded in paraffin.",
    expected_output={'ontology_id': "CHEBI:16236"},
    metadata=metadata("easy", "chemical_recognition")
)

paraffin = Case(
    name="paraffin",
    inputs="Sections were mounted onto gelatin-coated slides and air-dried overnight at room temperature and then processed for in situ hybridization as described elsewhere [1, 42], or post-fixed in formalin, dehydrated in a graded alcohol series, and embedded in paraffin.",
    expected_output={'ontology_id': "CHEBI:28872"},
    metadata=metadata("easy", "chemical_recognition")
)

gelatin = Case(
    name="gelatin",
    inputs="Sections were mounted onto gelatin-coated slides and air-dried overnight at room temperature and then processed for in situ hybridization as described elsewhere [1, 42], or post-fixed in formalin, dehydrated in a graded alcohol series, and embedded in paraffin.",
    expected_output={'ontology_id': "CHEBI:5291"},
    metadata=metadata("easy", "chemical_recognition")
)


def create_chebi_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create CHEBI chemical recognition evaluation dataset from CRAFT corpus."""
    cases = [
        water, glutaraldehyde, sodium_phosphate, paraformaldehyde, cholinergic,
        formalin, sucrose, alcohol, paraffin, gelatin
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )