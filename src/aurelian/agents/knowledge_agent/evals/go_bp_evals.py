"""GO_BP biological process recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class GoBpMetadata(Dict[str, Any]):
    """Metadata dictionary for GO_BP evaluations."""
    pass


# GO_BP evaluation cases from CRAFT corpus - extracted from real text
biological_regulation = Case(
    name="biological regulation",
    inputs="The subset of genes that normally control the proliferation, differentiation, and survival of striatal neurons [18-20] are therefore of considerable importance in ensuring adaptive behavior at maturity.",
    expected_output={'ontology_id': "GO:0065007"},
    metadata=metadata("medium", "biological_process_recognition")
)

cell_proliferation = Case(
    name="cell proliferation",
    inputs="The subset of genes that normally control the proliferation, differentiation, and survival of striatal neurons [18-20] are therefore of considerable importance in ensuring adaptive behavior at maturity.",
    expected_output={'ontology_id': "GO:0008283"},
    metadata=metadata("medium", "biological_process_recognition")
)

cognition = Case(
    name="cognition",
    inputs="Numbers of medium spiny neurons and ratios of these and less numerous striatal interneurons are critical variables that influence motor performance and aspects of cognition.",
    expected_output={'ontology_id': "GO:0050890"},
    metadata=metadata("easy", "biological_process_recognition")
)

telencephalon_development = Case(
    name="telencephalon development",
    inputs="Finally, recent experiments on the molecular control of telencephalic development have highlighted a number of genes that influence neuron proliferation and differentiation of the striatum and other neighboring forebrain structures [18][26-30].",
    expected_output={'ontology_id': "GO:0021537"},
    metadata=metadata("hard", "biological_process_recognition")
)

regulation_of_neurogenesis = Case(
    name="regulation of neurogenesis",
    inputs="The subset of genes that normally control the proliferation, differentiation, and survival of striatal neurons [18-20] are therefore of considerable importance in ensuring adaptive behavior at maturity.",
    expected_output={'ontology_id': "GO:0050767"},
    metadata=metadata("hard", "biological_process_recognition")
)

gene_expression = Case(
    name="gene expression",
    inputs="Striatal neurons are divided into two major subpopulations (patch and matrix), that have somewhat different gene expression profiles and have different patterns of pre- and postsynaptic connections [9-13].",
    expected_output={'ontology_id': "GO:0010467"},
    metadata=metadata("medium", "biological_process_recognition")
)

differentiation = Case(
    name="differentiation",
    inputs="The subset of genes that normally control the proliferation, differentiation, and survival of striatal neurons [18-20] are therefore of considerable importance in ensuring adaptive behavior at maturity.",
    expected_output={'ontology_id': "GO:0030154"},
    metadata=metadata("medium", "biological_process_recognition")
)

development = Case(
    name="development",
    inputs="Finally, recent experiments on the molecular control of telencephalic development have highlighted a number of genes that influence neuron proliferation and differentiation of the striatum and other neighboring forebrain structures [18][26-30].",
    expected_output={'ontology_id': "GO:0032502"},
    metadata=metadata("easy", "biological_process_recognition")
)

motor_behavior = Case(
    name="motor behavior",
    inputs="Numbers of medium spiny neurons and ratios of these and less numerous striatal interneurons are critical variables that influence motor performance and aspects of cognition.",
    expected_output={'ontology_id': "GO:0007626"},
    metadata=metadata("medium", "biological_process_recognition")
)

apoptosis = Case(
    name="apoptosis",
    inputs="Ears of Brn3c null mutants develop immature hair cells, identifiable only by certain molecular markers, and undergo apoptosis in neonates.",
    expected_output={'ontology_id': "GO:0006915"},
    metadata=metadata("medium", "biological_process_recognition")
)


def create_go_bp_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create GO_BP biological process recognition evaluation dataset from CRAFT corpus."""
    cases = [
        biological_regulation, cell_proliferation, cognition, telencephalon_development, 
        regulation_of_neurogenesis, gene_expression, differentiation, development, motor_behavior, apoptosis
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )