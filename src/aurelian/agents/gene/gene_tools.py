"""
Tools for retrieving gene information using the UniProt API and NCBI Entrez.
"""
from typing import Dict, List, Optional, Tuple, Any
import openai

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


def is_uniprot_id(gene_id: str) -> bool:
    """Check if the gene ID appears to be a UniProt accession.

    Args:
        gene_id: The gene ID to check

    Returns:
        True if it appears to be a UniProt ID, False otherwise
    """
    # UniProt IDs typically start with O, P, Q and contain numbers
    return gene_id.startswith(("P", "Q", "O")) and any(c.isdigit() for c in gene_id)


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
        if is_uniprot_id(gene_symbol):
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


def get_ncbi_gene_info(ctx: RunContext[GeneConfig], gene_id: str) -> Optional[str]:
    """Look up gene information in NCBI Entrez.

    Args:
        ctx: The run context with access to the config
        gene_id: Gene ID or symbol to look up

    Returns:
        Gene information from NCBI if found, or None if not found
    """
    config = ctx.deps or get_config()
    ncbi = config.get_ncbi_client()
    
    try:
        # First try to find the gene in NCBI gene database
        search_results = ncbi.ESearch("gene", gene_id)
        gene_ids = search_results.get('idlist', [])
        
        if not gene_ids:
            # Try a more specific search if we think this is a gene symbol
            search_results = ncbi.ESearch("gene", f"{gene_id}[Gene Symbol]")
            gene_ids = search_results.get('idlist', [])
            
        if gene_ids:
            gene_id = gene_ids[0]
            gene_data = ncbi.EFetch("gene", id=gene_id)
            return f"NCBI Entrez Gene Information:\n{gene_data}"
        
        # If not found in gene database, try protein database
        search_results = ncbi.ESearch("protein", gene_id)
        protein_ids = search_results.get('idlist', [])
        
        if protein_ids:
            protein_id = protein_ids[0]
            protein_data = ncbi.EFetch("protein", id=protein_id, rettype="fasta", retmode="text")
            try:
                # Strip byte prefix if present
                if isinstance(protein_data, bytes):
                    protein_data = protein_data.decode('utf-8')
                elif isinstance(protein_data, str) and protein_data.startswith('b\''):
                    protein_data = protein_data[2:-1].replace('\\n', '\n')
            except UnicodeDecodeError:
                pass
                
            # Get additional details with esummary
            summary_data = ncbi.ESummary("protein", id=protein_id)
            
            # Extract and format useful summary information
            protein_summary = ""
            if isinstance(summary_data, dict) and summary_data:
                # For newer versions of bioservices
                if protein_id in summary_data:
                    details = summary_data[protein_id]
                    title = details.get('title', 'No title available')
                    organism = details.get('organism', 'Unknown organism')
                    protein_summary = f"Title: {title}\nOrganism: {organism}\n\n"
                # For other data structures returned by ESummary
                else:
                    title = None
                    organism = None
                    
                    for key, value in summary_data.items():
                        if isinstance(value, dict):
                            if 'title' in value:
                                title = value['title']
                            if 'organism' in value:
                                organism = value['organism']
                    
                    if title or organism:
                        protein_summary = f"Title: {title or 'Not available'}\nOrganism: {organism or 'Unknown'}\n\n"
            
            combined_data = f"{protein_summary}{protein_data}"
            return f"NCBI Entrez Protein Information:\n{combined_data}"
            
        # Try nucleotide database as well
        search_results = ncbi.ESearch("nuccore", gene_id)
        nuccore_ids = search_results.get('idlist', [])
        
        if nuccore_ids:
            nuccore_id = nuccore_ids[0]
            nuccore_data = ncbi.EFetch("nuccore", id=nuccore_id, rettype="gb", retmode="text")
            try:
                if isinstance(nuccore_data, bytes):
                    nuccore_data = nuccore_data.decode('utf-8')
            except:
                pass
            return f"NCBI Entrez Nucleotide Information:\n{nuccore_data}"
        
        return None
    except Exception as e:
        # Return None if lookup fails
        return f"Error querying NCBI Entrez: {str(e)}"


def get_gene_description(ctx: RunContext[GeneConfig], gene_id: str) -> str:
    """Get description for a single gene ID, using UniProt and falling back to NCBI Entrez.

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
        uniprot_info = None
        ncbi_info = None
        
        # First try to look up UniProt accession if it looks like a gene symbol
        if not is_uniprot_id(gene_id):
            uniprot_id = lookup_uniprot_accession(ctx, gene_id)
            # If lookup succeeded (returned a different ID), use that for retrieval
            if uniprot_id != gene_id:
                gene_id = uniprot_id
        
        # Direct lookup for UniProt IDs
        if is_uniprot_id(gene_id):
            try:
                result = u.retrieve(gene_id, frmt="txt")
                if result and result.strip() != "":
                    uniprot_info = result
            except:
                pass  # If direct lookup fails, continue with search
        
        # If we don't have UniProt info yet, try the search
        if not uniprot_info:
            # Search for the gene
            search_query = f'gene:{gene_id} OR accession:{gene_id} OR id:{gene_id}'
            results = u.search(search_query, frmt="tsv", 
                            columns="accession,id,gene_names,organism,protein_name,function,cc_disease")
            
            if not results or results.strip() == "":
                # Try a broader search if the specific one failed
                search_query = gene_id
                results = u.search(search_query, frmt="tsv", 
                                columns="accession,id,gene_names,organism,protein_name,function,cc_disease")
                
                if results and results.strip() != "":
                    uniprot_info = results
        
        # Check NCBI Entrez if we couldn't find anything in UniProt
        if not uniprot_info or uniprot_info.strip() == "":
            ncbi_info = get_ncbi_gene_info(ctx, gene_id)
        
        # Combine results or use whichever source had information
        if uniprot_info and ncbi_info:
            return f"## UniProt Information\n{uniprot_info}\n\n## NCBI Information\n{ncbi_info}"
        elif uniprot_info:
            return uniprot_info
        elif ncbi_info:
            return ncbi_info
        else:
            raise ModelRetry(f"No gene information found for: {gene_id} in either UniProt or NCBI Entrez")
        
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
    
    try:
        if not gene_ids:
            raise ModelRetry("No gene IDs provided")
        
        results = []
        gene_info_dict = {}
        
        for gene_id in gene_ids:
            try:
                gene_info = get_gene_description(ctx, gene_id)
                results.append(f"## Gene: {gene_id}\n{gene_info}\n")
                gene_info_dict[gene_id] = gene_info
            except Exception as e:
                results.append(f"## Gene: {gene_id}\nError: {str(e)}\n")
        
        if not results:
            raise ModelRetry("No gene information found for any of the provided IDs")
        
        # Store the gene info dictionary in the context for other tools to use
        ctx.state.gene_info_dict = gene_info_dict
        
        return "\n".join(results)
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving gene descriptions: {str(e)}")


def parse_gene_list(gene_list: str) -> List[str]:
    """Parse a string containing gene IDs or symbols into a list.
    
    Args:
        gene_list: String of gene identifiers separated by commas, spaces, semicolons, or newlines
        
    Returns:
        List of gene identifiers
    """
    if not gene_list:
        return []
    
    # Replace common separators with a single delimiter for splitting
    for sep in [',', ';', '\n', '\t']:
        gene_list = gene_list.replace(sep, ' ')
    
    # Split on spaces and filter out empty strings
    genes = [g.strip() for g in gene_list.split(' ') if g.strip()]
    return genes


def get_genes_from_list(ctx: RunContext[GeneConfig], gene_list: str) -> str:
    """Get descriptions for multiple gene IDs provided as a string.

    Args:
        ctx: The run context with access to the config
        gene_list: String containing gene identifiers separated by commas, spaces, or newlines

    Returns:
        The gene descriptions in a structured tabular format
    """
    gene_ids = parse_gene_list(gene_list)
    
    if not gene_ids:
        raise ModelRetry("No gene IDs could be parsed from the input string")
    
    return get_gene_descriptions(ctx, gene_ids)


def analyze_gene_set(ctx: RunContext[GeneConfig], gene_list: str) -> str:
    """Analyze a set of genes and generate a biological summary of their properties and relationships.
    
    Args:
        ctx: The run context with access to the config
        gene_list: String containing gene identifiers separated by commas, spaces, or newlines
        
    Returns:
        A structured biological summary of the gene set
    """
    # First, get detailed information about each gene
    gene_descriptions = get_genes_from_list(ctx, gene_list)
    
    # Get the gene info dictionary from the context
    gene_info_dict = getattr(ctx.state, "gene_info_dict", {})
    
    if not gene_info_dict:
        raise ModelRetry("No gene information was found to analyze")
    
    gene_ids = list(gene_info_dict.keys())
    
    # Prepare a prompt for the LLM
    prompt = f"""Analyze the following set of genes and provide a detailed biological summary:

Gene IDs/Symbols: {', '.join(gene_ids)}

Gene Information:
{gene_descriptions}

Based on this information, provide a structured analysis covering:
1. Shared biological processes these genes may participate in
2. Potential protein-protein interactions or functional relationships
3. Common cellular localization patterns
4. Involvement in similar pathways
5. Coordinated activities or cooperative functions
6. Any disease associations that multiple genes in this set share

Focus particularly on identifying relationships between at least a pair of these genes.
If the genes appear unrelated, note this but try to identify any subtle connections based on their function.

Format the response with appropriate markdown headings and bullet points.
"""
    
    # Access OpenAI API to generate the analysis
    try:
        # Use the configured model name if available
        model_name = getattr(ctx.deps, "model_name", "gpt-4o") if ctx.deps else "gpt-4o"
        # Use the configured API key if available
        api_key = getattr(ctx.deps, "openai_api_key", None) if ctx.deps else None
        
        if api_key:
            openai.api_key = api_key
            
        # Create the completion using OpenAI API
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a biology expert analyzing gene sets to identify functional relationships."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Extract the response content
        return response.choices[0].message.content
    except Exception as e:
        raise ModelRetry(f"Error generating gene set analysis: {str(e)}")