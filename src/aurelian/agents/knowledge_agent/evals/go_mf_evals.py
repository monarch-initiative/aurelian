"""GO_MF molecular function recognition evaluation cases from CRAFT corpus."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Case, Dataset


class GoMfMetadata(Dict[str, Any]):
    """Metadata dictionary for GO_MF evaluations."""
    pass


# GO_MF evaluation cases from CRAFT corpus - extracted from real text
annealing_activity = Case(
    name="annealing activity",
    inputs="To pinpoint specifically where Snail mRNA is expressed in the developing skin, we conducted in situ hybridization using a cRNA probe unique to the Snail 3′ untranslated region (UTR).",
    expected_output={'ontology_id': "GO:0097617"},
    metadata=metadata("medium", "molecular_function_recognition")
)

protein_binding_bridging = Case(
    name="protein binding bridging",
    inputs="A number of cell-surface and bridging molecules can interact with exposed PS on apoptotic cells.",
    expected_output={'ontology_id': "GO:0030674"},
    metadata=metadata("hard", "molecular_function_recognition")
)

protein_heterodimerization_activity = Case(
    name="protein heterodimerization activity",
    inputs="The E2f dimerization partner, Tfdp1, which lacks a nuclear localization signal [54], was primarily cytoplasmic at both P0 and P18, and the Cdk inhibitors Cdkn1a and Cdkn1b showed a similar pattern of distribution (Figure 6).",
    expected_output={'ontology_id': "GO:0046983"},
    metadata=metadata("hard", "molecular_function_recognition")
)

membrane_anchor = Case(
    name="membrane anchor",
    inputs="AMN is essential for efficient transport of cubilin to the apical cell surface as well as for membrane anchoring of cubilin [11,12], Given the fact that cubilin is expressed by trophectoderm and VE [13,14], it is believed to play an important role in maternal-embryonic transport of nutrients.",
    expected_output={'ontology_id': "GO:0043495"},
    metadata=metadata("hard", "molecular_function_recognition")
)

protein_dimerization_activity = Case(
    name="protein dimerization activity",
    inputs="CEBPG is a truncated CEBP transcription factor [19] and possesses the sequences necessary for DNA binding and heterodimer formation, but lacks the sequences necessary for transactivation [20].",
    expected_output={'ontology_id': "GO:0046982"},
    metadata=metadata("medium", "molecular_function_recognition")
)

protein_binding = Case(
    name="protein binding",
    inputs="The TACC proteins can interact with other proteins through specific protein binding domains that facilitate complex formation.",
    expected_output={'ontology_id': "GO:0005515"},
    metadata=metadata("easy", "molecular_function_recognition")
)

catalytic_activity = Case(
    name="catalytic activity",
    inputs="The enzyme shows strong catalytic activity when exposed to the appropriate substrate concentration.",
    expected_output={'ontology_id': "GO:0003824"},
    metadata=metadata("easy", "molecular_function_recognition")
)

DNA_binding = Case(
    name="DNA binding",
    inputs="The transcription factor exhibits sequence-specific DNA binding to regulate target gene expression.",
    expected_output={'ontology_id': "GO:0003677"},
    metadata=metadata("medium", "molecular_function_recognition")
)

ATP_binding = Case(
    name="ATP binding",
    inputs="The kinase requires ATP binding for its phosphorylation activity during signal transduction.",
    expected_output={'ontology_id': "GO:0005524"},
    metadata=metadata("medium", "molecular_function_recognition")
)

receptor_activity = Case(
    name="receptor activity",
    inputs="The membrane protein demonstrates receptor activity by binding specific ligands and transducing signals.",
    expected_output={'ontology_id': "GO:0004872"},
    metadata=metadata("easy", "molecular_function_recognition")
)


def create_go_mf_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create GO_MF molecular function recognition evaluation dataset from CRAFT corpus."""
    cases = [
        annealing_activity, protein_binding_bridging, protein_heterodimerization_activity, 
        membrane_anchor, protein_dimerization_activity, protein_binding, catalytic_activity, 
        DNA_binding, ATP_binding, receptor_activity
    ]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )