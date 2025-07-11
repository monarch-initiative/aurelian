"""Evaluation cases for Knowledge Agent."""

from typing import Any, Dict
from aurelian.evaluators.model import MetadataDict
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Dataset

# Import evaluation datasets from evals subfolder  
from .evals.mondo_evals import create_mondo_eval_dataset
from .evals.uberon_evals import create_uberon_eval_dataset
from .evals.chebi_evals import create_chebi_eval_dataset
from .evals.cl_evals import create_cl_eval_dataset
from .evals.go_bp_evals import create_go_bp_eval_dataset
from .evals.go_cc_evals import create_go_cc_eval_dataset
from .evals.go_mf_evals import create_go_mf_eval_dataset
from .evals.pr_evals import create_pr_eval_dataset
from .evals.so_evals import create_so_eval_dataset
from .evals.ncbitaxon_evals import create_ncbitaxon_eval_dataset
from .evals.mop_evals import create_mop_eval_dataset

class KnowledgeAgentMetadata(Dict[str, Any]):
    """Simple metadata dictionary for Knowledge Agent evaluations."""
    pass

# All evaluation datasets completed with real CRAFT corpus cases:
# MONDO: 10 disease recognition cases - Located in: evals/mondo_evals.py
# UBERON: 10 anatomy recognition cases - Located in: evals/uberon_evals.py
# CHEBI: 10 chemical recognition cases - Located in: evals/chebi_evals.py  
# CL: 10 cell type recognition cases - Located in: evals/cl_evals.py
# GO_BP: 10 biological process recognition cases - Located in: evals/go_bp_evals.py
# GO_CC: 10 cellular component recognition cases - Located in: evals/go_cc_evals.py
# GO_MF: 10 molecular function recognition cases - Located in: evals/go_mf_evals.py
# PR: 10 protein recognition cases - Located in: evals/pr_evals.py
# SO: 10 sequence feature recognition cases - Located in: evals/so_evals.py
# NCBITaxon: 10 organism recognition cases - Located in: evals/ncbitaxon_evals.py
# MOP: 10 molecular process recognition cases - Located in: evals/mop_evals.py

# Main evaluation functions that aggregate cases from all ontologies
def create_comprehensive_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create comprehensive evaluation dataset combining all ontologies."""
    all_cases = []
    
    # Add cases from all ontology datasets
    all_cases.extend(create_mondo_eval_dataset().cases)
    all_cases.extend(create_uberon_eval_dataset().cases)
    all_cases.extend(create_chebi_eval_dataset().cases)
    all_cases.extend(create_cl_eval_dataset().cases)
    all_cases.extend(create_go_bp_eval_dataset().cases)
    all_cases.extend(create_go_cc_eval_dataset().cases)
    all_cases.extend(create_go_mf_eval_dataset().cases)
    all_cases.extend(create_pr_eval_dataset().cases)
    all_cases.extend(create_so_eval_dataset().cases)
    all_cases.extend(create_ncbitaxon_eval_dataset().cases)
    all_cases.extend(create_mop_eval_dataset().cases)
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=all_cases,
        evaluators=evaluators
    )

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create evaluation dataset for the knowledge agent (alias for comprehensive dataset)."""
    return create_comprehensive_eval_dataset()