"""
Tools for retrieving gene information using the UniProt API and NCBI Entrez.
"""
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field
import re
import openai
import time
import threading
import json
import os
import datetime
import logging

from pydantic_ai import RunContext, ModelRetry

from .talisman_config import TalismanConfig, get_config

# Define data models for structured output
class FunctionalTerm(BaseModel):
    """A functional term associated with genes."""
    term: str = Field(..., description="The biological term or concept")
    genes: List[str] = Field(..., description="List of genes associated with this term")
    source: str = Field(..., description="The source database or ontology (GO-BP, KEGG, Reactome, etc.)")

class GeneSummary(BaseModel):
    """Summary information for a gene."""
    id: str = Field(..., description="The gene identifier (Gene Symbol)")
    annotation: str = Field(..., description="Genomic coordinates or accession with position")
    genomic_context: str = Field(..., description="Information about genomic location (chromosome, etc.)")
    organism: str = Field(..., description="The organism the gene belongs to")
    description: str = Field(..., description="The protein/gene function description")

class GeneSetAnalysis(BaseModel):
    """Complete analysis of a gene set."""
    input_species: str = Field(default="", description="The species provided by the user")
    inferred_species: str = Field(default="", description="The species inferred from the gene data")
    narrative: str = Field(default="No narrative information available for these genes.", 
                          description="Explanation of functional and categorical relationships between genes")
    functional_terms: List[FunctionalTerm] = Field(default_factory=list, 
                                                 description="Functional terms associated with the gene set")
    gene_summaries: List[GeneSummary] = Field(default_factory=list, 
                                            description="Summary information for each gene")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] Talisman: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Rate limiting implementation
class RateLimiter:
    """Simple rate limiter to ensure we don't exceed API rate limits."""
    
    def __init__(self, max_calls: int = 3, period: float = 1.0):
        """
        Initialize the rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in the period
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = threading.Lock()
        
    def wait(self):
        """
        Wait if necessary to respect the rate limit.
        """
        with self.lock:
            now = time.time()
            
            # Remove timestamps older than the period
            self.calls = [t for t in self.calls if now - t < self.period]
            
            # If we've reached the maximum calls for this period, wait
            if len(self.calls) >= self.max_calls:
                # Calculate how long to wait
                oldest_call = min(self.calls)
                wait_time = self.period - (now - oldest_call)
                if wait_time > 0:
                    time.sleep(wait_time)
                # Reset calls after waiting
                self.calls = []
            
            # Add the current timestamp
            self.calls.append(time.time())

# Create rate limiters for UniProt and NCBI
uniprot_limiter = RateLimiter(max_calls=3, period=1.0)
ncbi_limiter = RateLimiter(max_calls=3, period=1.0)


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


def lookup_uniprot_accession(ctx: RunContext[TalismanConfig], gene_symbol: str) -> str:
    """Look up UniProt accession for a gene symbol.

    Args:
        ctx: The run context with access to the config
        gene_symbol: The gene symbol to look up

    Returns:
        UniProt accession if found, or the original symbol if not found
    """
    logging.info(f"Looking up UniProt accession for: {gene_symbol}")
    
    config = ctx.deps or get_config()
    u = config.get_uniprot_client()
    
    try:
        gene_symbol = normalize_gene_id(gene_symbol)
        
        # Skip lookup if it already looks like a UniProt ID
        if is_uniprot_id(gene_symbol):
            logging.info(f"{gene_symbol} appears to be a UniProt ID already")
            return gene_symbol
        
        # Apply rate limiting before making the request
        uniprot_limiter.wait()
        
        # Search for the gene symbol specifically
        logging.info(f"Searching UniProt for gene symbol: {gene_symbol}")
        search_query = f'gene:{gene_symbol} AND reviewed:yes'
        results = u.search(search_query, frmt="tsv", columns="accession,gene_names")
        
        if results and results.strip() != "":
            # Get the first line after the header and extract the accession
            lines = results.strip().split('\n')
            if len(lines) > 1:
                uniprot_id = lines[1].split('\t')[0]
                logging.info(f"Found UniProt accession: {uniprot_id} for {gene_symbol}")
                return uniprot_id
        
        logging.info(f"No UniProt accession found for {gene_symbol}, using original symbol")
        return gene_symbol
    except Exception as e:
        # Return original gene symbol if lookup fails
        logging.warning(f"Error looking up UniProt accession for {gene_symbol}: {str(e)}")
        return gene_symbol


def get_ncbi_gene_info(ctx: RunContext[TalismanConfig], gene_id: str, organism: str = None) -> Optional[str]:
    """Look up gene information in NCBI Entrez.

    Args:
        ctx: The run context with access to the config
        gene_id: Gene ID or symbol to look up
        organism: Optional organism name to restrict search (e.g., "Salmonella", "Homo sapiens")

    Returns:
        Gene information from NCBI if found, or None if not found
    """
    logging.info(f"Looking up NCBI information for: {gene_id}")
    
    config = ctx.deps or get_config()
    ncbi = config.get_ncbi_client()
    
    # No need to check for specific gene patterns
    
    # Set organisms to try without domain-specific knowledge
    organisms_to_try = [organism] if organism else [None]  # Use organism if provided, else try without organism constraint
    
    gene_results = None
    
    try:
        # Try for each organism in priority order
        for org in organisms_to_try:
            # First try to find the gene with organism constraint
            if org:
                logging.info(f"Searching NCBI gene database for: {gene_id} in organism: {org}")
                ncbi_limiter.wait()
                search_query = f"{gene_id}[Gene Symbol] AND {org}[Organism]"
                search_results = ncbi.ESearch("gene", search_query)
                gene_ids = search_results.get('idlist', [])
                
                if gene_ids:
                    gene_id_found = gene_ids[0]
                    logging.info(f"Found gene ID: {gene_id_found} in {org}, fetching details")
                    ncbi_limiter.wait()
                    gene_data = ncbi.EFetch("gene", id=gene_id_found)
                    gene_results = f"NCBI Entrez Gene Information:\n{gene_data}"
                    break
            
            # Try without organism constraint as fallback
            if not gene_results:
                logging.info(f"Trying gene symbol search without organism constraint for: {gene_id}")
                ncbi_limiter.wait()
                search_results = ncbi.ESearch("gene", f"{gene_id}[Gene Symbol]")
                gene_ids = search_results.get('idlist', [])
                
                if gene_ids:
                    gene_id_found = gene_ids[0]
                    logging.info(f"Found gene ID: {gene_id_found}, fetching details")
                    ncbi_limiter.wait()
                    gene_data = ncbi.EFetch("gene", id=gene_id_found)
                    gene_results = f"NCBI Entrez Gene Information:\n{gene_data}"
                    break
        
        # If we found gene results, return them
        if gene_results:
            return gene_results
        
        # If not found in gene database, try protein database
        # Standard protein search
        protein_ids = []
        for org in organisms_to_try:
            if org:
                logging.info(f"Searching NCBI protein database for: {gene_id} in organism: {org}")
                ncbi_limiter.wait()
                search_query = f"{gene_id} AND {org}[Organism]"
                search_results = ncbi.ESearch("protein", search_query)
                protein_ids = search_results.get('idlist', [])
                
                if protein_ids:
                    logging.info(f"Found protein ID(s) for {gene_id} in {org}: {protein_ids}")
                    break
        
        # If no results with organism constraint, try without
        if not protein_ids:
            logging.info(f"Searching NCBI protein database for: {gene_id}")
            ncbi_limiter.wait()
            search_results = ncbi.ESearch("protein", gene_id)
            protein_ids = search_results.get('idlist', [])
        
        if protein_ids:
            protein_id = protein_ids[0]
            logging.info(f"Found protein ID: {protein_id}, fetching sequence")
            ncbi_limiter.wait()
            protein_data = ncbi.EFetch("protein", id=protein_id, rettype="fasta", retmode="text")
            try:
                # Strip byte prefix if present
                if isinstance(protein_data, bytes):
                    protein_data = protein_data.decode('utf-8')
                elif isinstance(protein_data, str) and protein_data.startswith('b\''):
                    protein_data = protein_data[2:-1].replace('\\n', '\n')
            except:
                pass
                
            # Get additional details with esummary
            logging.info(f"Fetching protein summary for: {protein_id}")
            ncbi_limiter.wait()
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
                    logging.info(f"Found protein: {title} ({organism})")
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
                        if title:
                            logging.info(f"Found protein: {title}")
            
            combined_data = f"{protein_summary}{protein_data}"
            return f"NCBI Entrez Protein Information:\n{combined_data}"
            
        # Try nucleotide database as well
        logging.info(f"No protein found, trying NCBI nucleotide database for: {gene_id}")
        ncbi_limiter.wait()
        search_results = ncbi.ESearch("nuccore", gene_id)
        nuccore_ids = search_results.get('idlist', [])
        
        if nuccore_ids:
            nuccore_id = nuccore_ids[0]
            logging.info(f"Found nucleotide ID: {nuccore_id}, fetching details")
            ncbi_limiter.wait()
            nuccore_data = ncbi.EFetch("nuccore", id=nuccore_id, rettype="gb", retmode="text")
            try:
                if isinstance(nuccore_data, bytes):
                    nuccore_data = nuccore_data.decode('utf-8')
            except:
                pass
            return f"NCBI Entrez Nucleotide Information:\n{nuccore_data}"
        
        logging.info(f"No information found in NCBI for: {gene_id}")
        return None
    except Exception as e:
        # Return None if lookup fails
        logging.warning(f"Error querying NCBI Entrez for {gene_id}: {str(e)}")
        return f"Error querying NCBI Entrez: {str(e)}"


def ensure_complete_output(markdown_result: str, gene_set_analysis: GeneSetAnalysis) -> str:
    """Ensures that the markdown output has all required sections.
    
    Args:
        markdown_result: The original markdown result
        gene_set_analysis: The structured data model
        
    Returns:
        A complete markdown output with all required sections
    """
    logging.info("Post-processing output to ensure all sections are present")
    
    # Check if output already has proper sections - always enforce
    has_narrative = re.search(r'^\s*##\s*Narrative', markdown_result, re.MULTILINE) is not None
    has_functional_terms = re.search(r'^\s*##\s*Functional Terms Table', markdown_result, re.MULTILINE) is not None
    has_gene_summary = re.search(r'^\s*##\s*Gene Summary Table', markdown_result, re.MULTILINE) is not None
    has_species = re.search(r'^\s*#\s*Species', markdown_result, re.MULTILINE) is not None
    
    # We'll always rebuild the output to ensure consistent formatting
    result = ""
    
    # Add species section if applicable
    if gene_set_analysis.input_species or gene_set_analysis.inferred_species:
        result += "# Species\n"
        if gene_set_analysis.input_species:
            result += f"Input: {gene_set_analysis.input_species}\n"
        if gene_set_analysis.inferred_species:
            result += f"Inferred: {gene_set_analysis.inferred_species}\n"
        result += "\n"
    
    # Add main header
    result += "# Gene Set Analysis\n\n"
    
    # Add narrative section - always include
    result += "## Narrative\n"
    if has_narrative:
        # Extract existing narrative if it exists
        narrative_match = re.search(r'##\s*Narrative\s*\n(.*?)(?=^\s*##|\Z)', 
                                   markdown_result, re.MULTILINE | re.DOTALL)
        if narrative_match and narrative_match.group(1).strip():
            result += narrative_match.group(1).strip() + "\n\n"
        else:
            result += f"{gene_set_analysis.narrative}\n\n"
    else:
        # Use the narrative from the model
        result += f"{gene_set_analysis.narrative}\n\n"
    
    # Add functional terms table - always include
    result += "## Functional Terms Table\n"
    result += "| Functional Term | Genes | Source |\n"
    result += "|-----------------|-------|--------|\n"
    
    if has_functional_terms:
        # Try to extract existing table content
        ft_match = re.search(r'##\s*Functional Terms Table\s*\n\|.*\|\s*\n\|[-\s|]*\|\s*\n(.*?)(?=^\s*##|\Z)', 
                           markdown_result, re.MULTILINE | re.DOTALL)
        if ft_match and ft_match.group(1).strip():
            # Use existing content
            for line in ft_match.group(1).strip().split("\n"):
                if line.strip() and "|" in line:
                    result += line + "\n"
        elif gene_set_analysis.functional_terms:
            # Use model content
            for term in gene_set_analysis.functional_terms:
                genes_str = ", ".join(term.genes)
                result += f"| {term.term} | {genes_str} | {term.source} |\n"
        else:
            # Create default content
            gene_ids = [g.id for g in gene_set_analysis.gene_summaries]
            if gene_ids:
                result += f"| Gene set | {', '.join(gene_ids)} | Analysis |\n"
            else:
                result += "| No terms available | - | - |\n"
    else:
        # Always include functional terms, using content from model
        if gene_set_analysis.functional_terms:
            for term in gene_set_analysis.functional_terms:
                genes_str = ", ".join(term.genes)
                result += f"| {term.term} | {genes_str} | {term.source} |\n"
        else:
            # Create default content if model has none
            gene_ids = [g.id for g in gene_set_analysis.gene_summaries]
            if gene_ids:
                result += f"| Gene set | {', '.join(gene_ids)} | Analysis |\n"
            else:
                result += "| No terms available | - | - |\n"
    
    result += "\n"
    
    # Add gene summary table - always include
    result += "## Gene Summary Table\n"
    result += "| ID | Annotation | Genomic Context | Organism | Description |\n"
    result += "|-------------|-------------|----------|----------------|------------|\n"
    
    if has_gene_summary:
        # Try to extract existing gene summary
        gs_match = re.search(r'##\s*Gene Summary Table\s*\n\|.*\|\s*\n\|[-\s|]*\|\s*\n(.*?)(?=^\s*##|\Z)', 
                           markdown_result, re.MULTILINE | re.DOTALL)
        if gs_match and gs_match.group(1).strip():
            # Use existing content
            for line in gs_match.group(1).strip().split("\n"):
                if line.strip() and "|" in line:
                    result += line + "\n"
        elif gene_set_analysis.gene_summaries:
            # Use model content
            for gene in gene_set_analysis.gene_summaries:
                result += f"| {gene.id} | {gene.annotation} | {gene.genomic_context} | {gene.organism} | {gene.description} |\n"
        else:
            # Create default content
            result += "| No gene information available | - | - | - | - |\n"
    else:
        # Always include gene summary, using content from model
        if gene_set_analysis.gene_summaries:
            for gene in gene_set_analysis.gene_summaries:
                result += f"| {gene.id} | {gene.annotation} | {gene.genomic_context} | {gene.organism} | {gene.description} |\n"
        else:
            # Create default content if model has none
            result += "| No gene information available | - | - | - | - |\n"
    
    logging.info("Successfully enforced all required sections in the output")
    return result


def get_gene_description(ctx: RunContext[TalismanConfig], gene_id: str, organism: str = None) -> str:
    """Get description for a single gene ID, using UniProt and falling back to NCBI Entrez.

    Args:
        ctx: The run context with access to the config
        gene_id: The gene identifier (UniProt ID, gene symbol, etc.)
        organism: Optional organism name to restrict search (e.g., "Salmonella", "Homo sapiens")

    Returns:
        The gene description in a structured format
    """
    logging.info(f"Getting description for gene: {gene_id}")
    config = ctx.deps or get_config()
    u = config.get_uniprot_client()
    
    try:
        # Normalize the gene ID
        gene_id = normalize_gene_id(gene_id)
        logging.info(f"Normalized gene ID: {gene_id}")
        uniprot_info = None
        ncbi_info = None
        
        # First try to look up UniProt accession if it looks like a gene symbol
        if not is_uniprot_id(gene_id):
            logging.info(f"Not a UniProt ID, looking up accession for: {gene_id}")
            uniprot_id = lookup_uniprot_accession(ctx, gene_id)
            # If lookup succeeded (returned a different ID), use that for retrieval
            if uniprot_id != gene_id:
                logging.info(f"Using UniProt ID: {uniprot_id} instead of {gene_id}")
                gene_id = uniprot_id
        
        # Direct lookup for UniProt IDs
        if is_uniprot_id(gene_id):
            try:
                logging.info(f"Performing direct UniProt lookup for: {gene_id}")
                # Apply rate limiting
                uniprot_limiter.wait()
                result = u.retrieve(gene_id, frmt="txt")
                if result and result.strip() != "":
                    logging.info(f"Found direct UniProt entry for: {gene_id}")
                    uniprot_info = result
                else:
                    logging.info(f"No direct UniProt entry found for: {gene_id}")
            except Exception as e:
                logging.warning(f"Error in direct UniProt lookup: {str(e)}")
                pass  # If direct lookup fails, continue with search
        
        # If we don't have UniProt info yet, try the search
        if not uniprot_info:
            # Search for the gene
            logging.info(f"Performing UniProt search for: {gene_id}")
            uniprot_limiter.wait()
            search_query = f'gene:{gene_id} OR accession:{gene_id} OR id:{gene_id}'
            results = u.search(search_query, frmt="tsv", 
                            columns="accession,id,gene_names,organism,protein_name,function,cc_disease")
            
            if not results or results.strip() == "":
                # Try a broader search if the specific one failed
                logging.info(f"No specific match found, trying broader UniProt search for: {gene_id}")
                uniprot_limiter.wait()
                search_query = gene_id
                results = u.search(search_query, frmt="tsv", 
                                columns="accession,id,gene_names,organism,protein_name,function,cc_disease")
                
                if results and results.strip() != "":
                    logging.info(f"Found UniProt entries in broader search for: {gene_id}")
                    uniprot_info = results
                else:
                    logging.info(f"No UniProt entries found in broader search for: {gene_id}")
            else:
                logging.info(f"Found UniProt entries in specific search for: {gene_id}")
                uniprot_info = results
        
        # Check NCBI Entrez if we couldn't find anything in UniProt
        if not uniprot_info or uniprot_info.strip() == "":
            logging.info(f"No UniProt information found, checking NCBI for: {gene_id}")
            # Pass the organism if we have one or auto-detected one
            ncbi_info = get_ncbi_gene_info(ctx, gene_id, organism)
            if ncbi_info:
                logging.info(f"Found NCBI information for: {gene_id}")
            else:
                logging.warning(f"No NCBI information found for: {gene_id}")
        
        # Combine results or use whichever source had information
        if uniprot_info and ncbi_info:
            logging.info(f"Returning combined UniProt and NCBI information for: {gene_id}")
            return f"## UniProt Information\n{uniprot_info}\n\n## NCBI Information\n{ncbi_info}"
        elif uniprot_info:
            logging.info(f"Returning UniProt information for: {gene_id}")
            return uniprot_info
        elif ncbi_info:
            logging.info(f"Returning NCBI information for: {gene_id}")
            return ncbi_info
        else:
            logging.error(f"No gene information found for: {gene_id} in either UniProt or NCBI")
            raise ModelRetry(f"No gene information found for: {gene_id} in either UniProt or NCBI Entrez")
        
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        logging.error(f"Error retrieving gene description for {gene_id}: {str(e)}")
        raise ModelRetry(f"Error retrieving gene description: {str(e)}")


def get_gene_descriptions(ctx: RunContext[TalismanConfig], gene_ids: List[str]) -> str:
    """Get descriptions for multiple gene IDs.

    Args:
        ctx: The run context with access to the config
        gene_ids: List of gene identifiers

    Returns:
        The gene descriptions in a structured tabular format
    """
    logging.info(f"Retrieving descriptions for {len(gene_ids)} genes: {', '.join(gene_ids)}")
    config = ctx.deps or get_config()
    
    try:
        if not gene_ids:
            logging.error("No gene IDs provided")
            raise ModelRetry("No gene IDs provided")
        
        results = []
        gene_info_dict = {}
        
        for i, gene_id in enumerate(gene_ids):
            logging.info(f"Processing gene {i+1}/{len(gene_ids)}: {gene_id}")
            try:
                gene_info = get_gene_description(ctx, gene_id)
                results.append(f"## Gene: {gene_id}\n{gene_info}\n")
                gene_info_dict[gene_id] = gene_info
                logging.info(f"Successfully retrieved information for {gene_id}")
            except Exception as e:
                logging.warning(f"Error retrieving information for {gene_id}: {str(e)}")
                results.append(f"## Gene: {gene_id}\nError: {str(e)}\n")
        
        if not results:
            logging.error("No gene information found for any of the provided IDs")
            raise ModelRetry("No gene information found for any of the provided IDs")
        
        # Store the gene info dictionary in an attribute we add to ctx (state only available in test context)
        # Use hasattr to check if the attribute already exists
        if not hasattr(ctx, "gene_info_dict"):
            # Create the attribute if it doesn't exist
            setattr(ctx, "gene_info_dict", {})
        
        # Now set the value
        ctx.gene_info_dict = gene_info_dict
        logging.info(f"Successfully retrieved information for {len(gene_info_dict)} genes")
        
        return "\n".join(results)
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        logging.error(f"Error retrieving gene descriptions: {str(e)}")
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


def get_genes_from_list(ctx: RunContext[TalismanConfig], gene_list: str) -> str:
    """Get descriptions for multiple gene IDs provided as a string.

    Args:
        ctx: The run context with access to the config
        gene_list: String containing gene identifiers separated by commas, spaces, or newlines

    Returns:
        The gene descriptions in a structured tabular format
    """
    logging.info(f"Parsing gene list: {gene_list}")
    gene_ids = parse_gene_list(gene_list)
    
    if not gene_ids:
        logging.error("No gene IDs could be parsed from the input string")
        raise ModelRetry("No gene IDs could be parsed from the input string")
    
    logging.info(f"Parsed {len(gene_ids)} gene IDs: {', '.join(gene_ids)}")
    return get_gene_descriptions(ctx, gene_ids)


def analyze_gene_set(ctx: RunContext[TalismanConfig], gene_list: str) -> str:
    """Analyze a set of genes and generate a biological summary of their properties and relationships.
    
    Args:
        ctx: The run context with access to the config
        gene_list: String containing gene identifiers separated by commas, spaces, or newlines
        
    Returns:
        A structured biological summary of the gene set with Narrative, Functional Terms Table, and Gene Summary Table
    """
    logging.info(f"Starting gene set analysis for: {gene_list}")
    
    # Parse the gene list
    gene_ids_list = parse_gene_list(gene_list)
    organism = None  # Let the gene lookup systems determine the organism
    
    # First, get detailed information about each gene
    logging.info("Retrieving gene descriptions...")
    # Pass organism information to each gene lookup
    for gene_id in gene_ids_list:
        logging.info(f"Processing {gene_id} with organism context: {organism}")
        get_gene_description(ctx, gene_id, organism)
    
    # Now get all gene descriptions
    gene_descriptions = get_genes_from_list(ctx, gene_list)
    logging.info("Gene descriptions retrieved successfully")
    
    # Get the gene info dictionary from the context
    gene_info_dict = getattr(ctx, "gene_info_dict", {})
    
    if not gene_info_dict:
        logging.error("No gene information was found to analyze")
        raise ModelRetry("No gene information was found to analyze")
    
    gene_ids = list(gene_info_dict.keys())
    logging.info(f"Analyzing relationships between {len(gene_ids)} genes: {', '.join(gene_ids)}")
    
    # Extract organism information from the gene descriptions if possible
    detected_organism = None
    organism_keywords = ["Salmonella", "Escherichia", "Desulfovibrio", "Homo sapiens", "human"]
    for gene_info in gene_info_dict.values():
        for keyword in organism_keywords:
            if keyword.lower() in gene_info.lower():
                detected_organism = keyword
                break
        if detected_organism:
            break
    
    if detected_organism:
        logging.info(f"Detected organism from gene descriptions: {detected_organism}")
    
    # Prepare a prompt for the LLM with minimal instructions (main instructions are in the agent system prompt)
    prompt = f"""Analyze the following set of genes:

Gene IDs/Symbols: {', '.join(gene_ids)}

Gene Information:
{gene_descriptions}

{f"IMPORTANT: These genes are from {detected_organism or organism}. Make sure your analysis reflects the correct organism context." if detected_organism or organism else ""}

Please provide a comprehensive analysis of the genes."""
    
    # Access OpenAI API to generate the analysis
    try:
        # Use the configured model name if available
        model_name = getattr(ctx.deps, "model_name", "gpt-4o") if ctx.deps else "gpt-4o"
        # Use the configured API key if available
        api_key = getattr(ctx.deps, "openai_api_key", None) if ctx.deps else None
        
        logging.info(f"Generating biological analysis using model: {model_name}")
        
        if api_key:
            openai.api_key = api_key
            
        # Create the completion using OpenAI API
        system_prompt = """
You are a biology expert analyzing gene sets. You must provide a comprehensive analysis in JSON format.

Your response must be in this structured format:
{
  "narrative": "Detailed explanation of functional relationships between genes, emphasizing shared functions",
  "functional_terms": [
    {"term": "DNA damage response", "genes": ["BRCA1", "BRCA2", "ATM"], "source": "GO-BP"},
    {"term": "Homologous recombination", "genes": ["BRCA1", "BRCA2"], "source": "Reactome"},
    etc.
  ],
  "gene_summaries": [
    {
      "id": "BRCA1", 
      "annotation": "NC_000017.11 (43044295..43170327, complement)", 
      "genomic_context": "Chromosome 17", 
      "organism": "Homo sapiens", 
      "description": "Breast cancer type 1 susceptibility protein"
    },
    etc.
  ]
}

Your output MUST be valid JSON with these three fields. Do not include any text before or after the JSON.
"""
            
        logging.info("Sending request to OpenAI API...")
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        logging.info("Received response from OpenAI API")
        
        # Extract the response content
        response_content = response.choices[0].message.content
        
        try:
            # Try to parse the JSON response into our Pydantic model
            gene_set_analysis = GeneSetAnalysis.model_validate_json(response_content)
            json_result = response_content
            is_structured = True
            logging.info("Successfully parsed structured JSON response")
        except Exception as parse_error:
            # If JSON parsing fails, handle the unstructured text response
            logging.warning(f"Failed to parse JSON response: {str(parse_error)}. Creating structured format from text.")
            is_structured = False
            
            # Parse the unstructured text to extract information - look for Gene Summary Table section
            lines = response_content.split('\n')
            
            # Extract gene IDs from the table if present
            gene_ids_found = []
            description_map = {}
            organism_map = {}
            annotation_map = {}
            genomic_context_map = {}
            
            in_table = False
            for i, line in enumerate(lines):
                if "## Gene Summary Table" in line:
                    in_table = True
                    continue
                if in_table and '|' in line:
                    # Skip the header and separator lines
                    if "---" in line or "ID" in line:
                        continue
                    
                    # Parse the table row
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 6:  # Should have 6 parts with empty first and last elements
                        gene_id = parts[1].strip()
                        if gene_id:
                            gene_ids_found.append(gene_id)
                            description_map[gene_id] = parts[5].strip()
                            organism_map[gene_id] = parts[4].strip()
                            annotation_map[gene_id] = parts[2].strip()
                            genomic_context_map[gene_id] = parts[3].strip()
            
            # Extract any existing narrative from the output
            existing_narrative = "\n".join(
                [l for l in lines if not (
                    "## Gene Summary Table" in l or 
                    "## Functional Terms Table" in l or
                    "## Terms" in l or
                    (in_table and '|' in l)
                )]
            ).strip()
            
            # Use existing narrative if it exists and is substantial
            if existing_narrative and len(existing_narrative.split()) > 10:
                narrative = existing_narrative
            # Otherwise create a generic narrative from the gene info we have
            elif len(gene_ids_found) > 0:
                gene_ids_str = ", ".join(gene_ids_found)
                descriptions = [f"{g}: {description_map.get(g, 'Unknown function')}" for g in gene_ids_found]
                common_organism = next(iter(set(organism_map.values())), "Unknown organism")
                
                narrative = f"""The genes {gene_ids_str} are from {common_organism}.

Gene functions: {'; '.join(descriptions)}.

Based on their annotations and genomic context, these genes may be functionally related and potentially participate in shared biological pathways or cellular processes."""
            else:
                narrative = "No gene information available."
            
            # Create generic functional terms based on gene descriptions
            functional_terms = []
            
            # If we have gene IDs and descriptions, create a basic functional term
            if gene_ids_found:
                # Create a default functional term with all genes
                functional_terms.append({
                    "term": "Gene set",
                    "genes": gene_ids_found,
                    "source": "Analysis"
                })
                
                # Only extract functional terms from descriptions, without hardcoded knowledge
                for gene_id in gene_ids_found:
                    description = description_map.get(gene_id, "").lower()
                    if description and len(description) > 3:
                        functional_terms.append({
                            "term": f"{gene_id} function",
                            "genes": [gene_id],
                            "source": "Annotation"
                        })
            
            # Create gene summaries
            gene_summaries = []
            for gene_id in gene_ids_found:
                gene_summaries.append({
                    "id": gene_id,
                    "annotation": annotation_map.get(gene_id, "Unknown"),
                    "genomic_context": genomic_context_map.get(gene_id, "Unknown"),
                    "organism": organism_map.get(gene_id, "Unknown"),
                    "description": description_map.get(gene_id, "Unknown")
                })
            
            # Create a structured response
            structured_data = {
                "narrative": narrative,
                "functional_terms": functional_terms,
                "gene_summaries": gene_summaries
            }
            
            # Convert to JSON
            json_result = json.dumps(structured_data, indent=2)
            
            # Create the Pydantic model
            gene_set_analysis = GeneSetAnalysis.model_validate(structured_data)
        
        # Format the results in markdown for display
        markdown_result = "# Gene Set Analysis\n\n"
        
        # Add narrative section (always include this)
        narrative = gene_set_analysis.narrative.strip()
        if narrative:
            markdown_result += f"## Narrative\n{narrative}\n\n"
        else:
            # Create a generic narrative based on gene data without domain-specific information
            gene_ids = [g.id for g in gene_set_analysis.gene_summaries]
            gene_descs = [f"{g.id}: {g.description}" for g in gene_set_analysis.gene_summaries]
            organisms = list(set([g.organism for g in gene_set_analysis.gene_summaries]))
            
            if gene_set_analysis.gene_summaries:
                organism_str = organisms[0] if organisms else "Unknown organism"
                markdown_result += f"""## Narrative
The genes {', '.join(gene_ids)} are from {organism_str}.

Gene functions: {'; '.join(gene_descs)}.

Based on their annotations and genomic context, these genes may be functionally related and could potentially participate in shared biological pathways or cellular processes.
\n\n"""
            else:
                markdown_result += f"""## Narrative
No gene information available.
\n\n"""
        
        # Add functional terms table
        markdown_result += "## Functional Terms Table\n"
        markdown_result += "| Functional Term | Genes | Source |\n"
        markdown_result += "|-----------------|-------|--------|\n"
        
        # Add functional terms rows
        if gene_set_analysis.functional_terms:
            for term in gene_set_analysis.functional_terms:
                genes_str = ", ".join(term.genes)
                markdown_result += f"| {term.term} | {genes_str} | {term.source} |\n"
        else:
            # Add default terms if none exist
            gene_ids = [g.id for g in gene_set_analysis.gene_summaries]
            markdown_result += f"| Protein function | {', '.join(gene_ids)} | Literature |\n"
        
        # Add gene summary table
        markdown_result += "\n## Gene Summary Table\n"
        markdown_result += "| ID | Annotation | Genomic Context | Organism | Description |\n"
        markdown_result += "|-------------|-------------|----------|----------------|------------|\n"
        
        # Add gene summary rows
        for gene in gene_set_analysis.gene_summaries:
            markdown_result += f"| {gene.id} | {gene.annotation} | {gene.genomic_context} | {gene.organism} | {gene.description} |\n"
        
        # Save the results
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create both JSON and markdown files
        results_dir = os.path.join(os.path.expanduser("~"), "talisman_results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Save the JSON response
        json_path = os.path.join(results_dir, f"talisman_analysis_{timestamp}.json")
        with open(json_path, 'w') as f:
            f.write(json_result)
        
        # Save the markdown formatted response
        md_path = os.path.join(results_dir, f"talisman_analysis_{timestamp}.md")
        with open(md_path, 'w') as f:
            f.write(markdown_result)
            
        logging.info(f"Analysis complete. Results saved to: {json_path} and {md_path}")
        
        # Ensure all required sections are present in the markdown output
        final_output = ensure_complete_output(markdown_result, gene_set_analysis)
        
        # Return the post-processed markdown-formatted result for display
        return final_output
    except Exception as e:
        logging.error(f"Error generating gene set analysis: {str(e)}")
        raise ModelRetry(f"Error generating gene set analysis: {str(e)}")