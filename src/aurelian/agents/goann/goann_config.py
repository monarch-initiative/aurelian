"""
Configuration classes for the GO Annotation Review agent.
"""
from dataclasses import dataclass, field
from typing import Dict, Any

from bioservices import UniProt
from oaklib import get_adapter
from oaklib.implementations import AmiGOImplementation

from aurelian.dependencies.workdir import HasWorkdir
from aurelian.agents.uniprot.uniprot_tools import normalize_uniprot_id

# Initialize UniProt service
uniprot_service = UniProt(verbose=False)


@dataclass
class GOAnnotationDependencies(HasWorkdir):
    """
    Configuration for the GO Annotation Review agent.
    
    Args:
        taxon: NCBI Taxonomy ID, defaults to human (9606)
    """
    taxon: str = field(default="9606")

    # Options for the bioservices UniProt client
    uniprot_client_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.uniprot_client_options is None or len(self.uniprot_client_options) == 0:
            self.uniprot_client_options = {"verbose": False}

    def get_uniprot_client(self) -> UniProt:
        """Get a configured UniProt client."""
        return UniProt(**self.uniprot_client_options)
    
    def get_amigo_adapter(self) -> AmiGOImplementation:
        """
        Get the AmiGO adapter for the specified taxon.
        
        Returns:
            AmiGOImplementation: The OAK AmiGO adapter
        """
        return get_adapter(f"amigo:NCBITaxon:{self.taxon}")
        
    def get_gene_id(self, gene_term: str) -> str:
        """
        Normalize a gene identifier.
        
        Args:
            gene_term: The gene identifier
            
        Returns:
            str: The normalized gene identifier
        """
        return gene_term


def normalize_pmid(pmid: str) -> str:
    """
    Normalize a PubMed ID to the format PMID:nnnnnnn.
    
    Args:
        pmid: The PubMed ID
        
    Returns:
        str: The normalized PubMed ID
    """
    if ":" in pmid:
        pmid = pmid.split(":", 1)[1]
    if not pmid.startswith("PMID:"):
        pmid = f"PMID:{pmid}"
    return pmid


def get_config(taxon: str = "9606") -> GOAnnotationDependencies:
    """
    Get the GO Annotation Review configuration.
    
    Args:
        taxon: NCBI Taxonomy ID, defaults to human (9606)
        
    Returns:
        GOAnnotationDependencies: The GO Annotation dependencies
    """
    return GOAnnotationDependencies(taxon=taxon)