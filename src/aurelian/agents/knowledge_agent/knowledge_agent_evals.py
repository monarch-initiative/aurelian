"""Evaluation cases for Knowledge Agent."""

from typing import Any, Dict, Optional, List
from aurelian.evaluators.model import MetadataDict
from aurelian.evaluators.knowledge_agent_evaluator import SimpleEntityEvaluator
from pydantic_evals import Dataset

# Import evaluation datasets from evals subfolder  
from .evals.mondo_simple.mondo_evals import create_mondo_eval_dataset
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

def create_eval_dataset(
    difficulty: Optional[List[str]] = None,
    limit: Optional[int] = None,
    benchmark: Optional[str] = None
) -> Dataset[str, str, MetadataDict]:
    """Create evaluation dataset for the knowledge agent with optional filtering.
    
    Args:
        difficulty: Filter by difficulty levels (easy, medium, hard)
        limit: Limit number of cases to run
        benchmark: Run specific benchmark subset (e.g., 'mondo', 'uberon', etc.)
    """
    if benchmark:
        # Map benchmark names to their dataset functions
        benchmark_map = {
            'mondo': create_mondo_eval_dataset,
            'uberon': create_uberon_eval_dataset,
            'chebi': create_chebi_eval_dataset,
            'cl': create_cl_eval_dataset,
            'go_bp': create_go_bp_eval_dataset,
            'go_cc': create_go_cc_eval_dataset,
            'go_mf': create_go_mf_eval_dataset,
            'pr': create_pr_eval_dataset,
            'so': create_so_eval_dataset,
            'ncbitaxon': create_ncbitaxon_eval_dataset,
            'mop': create_mop_eval_dataset,
        }
        
        if benchmark in benchmark_map:
            dataset = benchmark_map[benchmark]()
            cases = dataset.cases
        else:
            raise ValueError(f"Unknown benchmark: {benchmark}. Available: {list(benchmark_map.keys())}")
    else:
        # Use comprehensive dataset
        dataset = create_comprehensive_eval_dataset()
        cases = dataset.cases
    
    # Apply difficulty filtering if specified
    if difficulty:
        filtered_cases = []
        for case in cases:
            case_difficulty = case.metadata.get('difficulty', 'medium')
            if case_difficulty in difficulty:
                filtered_cases.append(case)
        cases = filtered_cases
    
    # Apply limit if specified
    if limit:
        cases = cases[:limit]
    
    evaluators = [SimpleEntityEvaluator()]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )