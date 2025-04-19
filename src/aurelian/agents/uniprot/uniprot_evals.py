"""
Evaluation module for the UniProt agent.

This module implements evaluations for the UniProt agent using the pydantic-ai-evals framework.
"""
import asyncio
import sys
from typing import Optional, Any, Dict, Callable, Awaitable

from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

from aurelian.agents.uniprot.uniprot_agent import uniprot_agent
from aurelian.agents.uniprot.uniprot_config import UniprotConfig

class UniprotMetadata(Dict[str, Any]):
    """Simple metadata dictionary for UniProt evaluations."""
    pass

# Define individual evaluation cases
case1 = Case(
    name="human_insulin",
    inputs="Search for human insulin protein",
    expected_output="P01308",  # Human insulin UniProt ID
    metadata=metadata("easy", "protein_search")
)

case2 = Case(
    name="uniprot_entry_lookup",
    inputs="Look up UniProt entry P01308",
    expected_output="insulin",  # Should identify this as insulin
    metadata=metadata("easy", "id_lookup"),
    evaluators=[
        LLMJudge(
            rubric="""
            Answer should:
            1. Correctly identify P01308 as human insulin
            2. Include key information about the protein's function
            3. Mention its role in glucose homeostasis
            4. Provide information about protein structure
            """,
            include_input=True
        )
    ]
)

case3 = Case(
    name="id_mapping",
    inputs="Map UniProt IDs P01308,P01009 to PDB database",
    expected_output="PDB",  # Should return PDB IDs
    metadata=metadata("medium", "database_mapping")
)

case4 = Case(
    name="domain_identification",
    inputs="What domains are present in UniProt entry P53_HUMAN?",
    expected_output="domain",  # Should discuss protein domains
    metadata=metadata("medium", "protein_domain_analysis")
)

case5 = Case(
    name="disease_association",
    inputs="Find all proteins related to Alzheimer's disease",
    expected_output="amyloid",  # Should mention amyloid proteins
    metadata=metadata("hard", "disease_association_query")
)

def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """
    Create a dataset for evaluating the UniProt agent.
    
    Returns:
        Dataset of UniProt evaluation cases with appropriate evaluators
    """
    # Collect all cases
    cases = [case1, case2, case3, case4, case5]
    
    # Dataset-level evaluators
    evaluators = [
        SubstringEvaluator(),
        LLMJudge(
            rubric="""
            Evaluate the answer based on:
            1. Accuracy of protein information provided
            2. Correct identification of UniProt IDs and cross-references
            3. Comprehensive coverage of protein structure and function
            4. Proper description of protein domains and modifications
            5. Accurate representation of protein-disease associations
            """,
            model="anthropic:claude-3-7-sonnet-latest"
        )
    ]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )