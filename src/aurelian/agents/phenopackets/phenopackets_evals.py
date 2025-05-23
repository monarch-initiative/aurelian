"""
Evaluation module for the Phenopackets agent.

This module implements evaluations for the Phenopackets agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

from aurelian.agents.phenopackets.phenopackets_agent import phenopackets_agent
from aurelian.agents.phenopackets.phenopackets_config import PhenopacketsDependencies

class PhenopacketsMetadata(Dict[str, Any]):
    """Simple metadata dictionary for Phenopackets evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="liver_disease_patients",
    inputs="What patients have liver disease?",
    expected_output="hepat",  # Should mention hepatic/liver terms
    metadata=metadata("medium", "phenotype_query")
)

case2 = Case(
    name="metabolic_pathway_genes",
    inputs="What phenopackets involve genes from metabolic pathways?",
    expected_output="metabol",  # Should mention metabolic genes/pathways
    metadata=metadata("hard", "gene_pathway_query"),
    evaluators=[
        LLMJudge(
            rubric="""
            Answer should:
            1. Identify phenopackets containing genes involved in metabolic pathways
            2. Link the metabolic genes to their corresponding phenotypes
            3. Explain how these genes relate to metabolic pathways
            4. Provide patient/case IDs where applicable
            """,
            include_input=True
        )
    ]
)

case3 = Case(
    name="variant_effect_peroxisomal",
    inputs="How does the type of variant affect phenotype in peroxisomal disorders?",
    expected_output="peroxisom",  # Should discuss peroxisomal disorders
    metadata=metadata("hard", "variant_phenotype_correlation")
)

case4 = Case(
    name="skeletal_dysplasia_comparison",
    inputs="Examine phenopackets for skeletal dysplasias and compare their phenotypes",
    expected_output="skeletal",  # Should discuss skeletal terms
    metadata=metadata("medium", "comparative_phenotype_analysis")
)

case5 = Case(
    name="pnpla6_mutations",
    inputs="Look up any patients with mutations in the PNPLA6 gene",
    expected_output="PNPLA6",  # Should mention the PNPLA6 gene
    metadata=metadata("easy", "gene_mutation_query")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the Phenopackets agent.
    
    Returns:
        Dataset of Phenopackets evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4, case5]
    
    # Dataset-level evaluators
    evaluators = [
        SubstringEvaluator(),
        LLMJudge(
            rubric="""
            Evaluate the answer based on:
            1. Accuracy in identifying relevant phenopackets based on the query
            2. Correct interpretation of phenotype-genotype relationships
            3. Proper use of HPO terms and gene identifiers
            4. Comprehensive analysis of phenotypic data when requested
            5. Clear presentation of results including patient/case identifiers when appropriate
            """,
            model="anthropic:claude-3-7-sonnet-latest"
        )
    ]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )