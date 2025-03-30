"""
Tools for retrieving gene information using the UniProt API.
"""
from typing import Dict, List, Optional

from pydantic_ai import RunContext, ModelRetry

from .gene_config import GeneConfig, get_config


def normalize_gene_id(gene_id: str) -> str:
    """Normalize a gene ID by removing any version number or prefix.

    Args:
        gene_id: The gene ID

    Returns:
        The normalized gene ID
    """
    if ":" in gene_id:
        return gene_id.split(":")[-1]
    return gene_id


def lookup_uniprot_accession(ctx: RunContext[GeneConfig], gene_symbol: str) -> str:
    """Look up UniProt accession for a gene symbol.

    Args:
        ctx: The run context with access to the config
        gene_symbol: The gene symbol to look up

    Returns:
        UniProt accession if found, or the original symbol if not found
    """
    config = ctx.deps or get_config()
    u = config.get_uniprot_client()
    
    try:
        gene_symbol = normalize_gene_id(gene_symbol)
        
        # Skip lookup if it already looks like a UniProt ID
        if gene_symbol.startswith(("P", "Q", "O")) and any(c.isdigit() for c in gene_symbol):
            return gene_symbol
        
        # Search for the gene symbol specifically
        search_query = f'gene:{gene_symbol} AND reviewed:yes'
        results = u.search(search_query, frmt="tsv", columns="accession,gene_names")
        
        if results and results.strip() != "":
            # Get the first line after the header and extract the accession
            lines = results.strip().split('\n')
            if len(lines) > 1:
                return lines[1].split('\t')[0]
        
        return gene_symbol
    except Exception:
        # Return original gene symbol if lookup fails
        return gene_symbol


def get_gene_description(ctx: RunContext[GeneConfig], gene_id: str) -> str:
    """Get description for a single gene ID.

    Args:
        ctx: The run context with access to the config
        gene_id: The gene identifier (UniProt ID, gene symbol, etc.)

    Returns:
        The gene description in a structured format
    """
    config = ctx.deps or get_config()
    u = config.get_uniprot_client()
    
    try:
        # Normalize the gene ID
        gene_id = normalize_gene_id(gene_id)
        
        # First try to look up UniProt accession if it looks like a gene symbol
        if not (gene_id.startswith(("P", "Q", "O")) and any(c.isdigit() for c in gene_id)):
            uniprot_id = lookup_uniprot_accession(ctx, gene_id)
            # If lookup succeeded (returned a different ID), use that for retrieval
            if uniprot_id != gene_id:
                gene_id = uniprot_id
        
        # Direct lookup for UniProt IDs
        if gene_id.startswith(("P", "Q", "O")) and any(c.isdigit() for c in gene_id):
            try:
                result = u.retrieve(gene_id, frmt="txt")
                if result and result.strip() != "":
                    return result
            except:
                pass  # If direct lookup fails, continue with search
        
        # Search for the gene
        search_query = f'gene:{gene_id} OR accession:{gene_id} OR id:{gene_id}'
        results = u.search(search_query, frmt="tsv", 
                         columns="accession,id,gene_names,organism,protein_name,function,cc_disease")
        
        if not results or results.strip() == "":
            # Try a broader search if the specific one failed
            search_query = gene_id
            results = u.search(search_query, frmt="tsv", 
                              columns="accession,id,gene_names,organism,protein_name,function,cc_disease")
            
            if not results or results.strip() == "":
                raise ModelRetry(f"No gene information found for: {gene_id}")
        
        return results
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving gene description: {str(e)}")


def get_gene_descriptions(ctx: RunContext[GeneConfig], gene_ids: List[str]) -> str:
    """Get descriptions for multiple gene IDs.

    Args:
        ctx: The run context with access to the config
        gene_ids: List of gene identifiers

    Returns:
        The gene descriptions in a structured tabular format
    """
    config = ctx.deps or get_config()
    u = config.get_uniprot_client()
    
    try:
        if not gene_ids:
            raise ModelRetry("No gene IDs provided")
        
        results = []
        for gene_id in gene_ids:
            try:
                gene_info = get_gene_description(ctx, gene_id)
                results.append(f"## Gene: {gene_id}\n{gene_info}\n")
            except Exception as e:
                results.append(f"## Gene: {gene_id}\nError: {str(e)}\n")
        
        if not results:
            raise ModelRetry("No gene information found for any of the provided IDs")
        
        return "\n".join(results)
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving gene descriptions: {str(e)}")