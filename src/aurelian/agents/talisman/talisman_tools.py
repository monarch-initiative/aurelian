"""
Tools for retrieving gene information using the UniProt API and NCBI Entrez.
"""
from typing import Dict, List, Optional, Tuple, Any
import openai
import time
import threading
import json
import os
import datetime
import logging

from pydantic_ai import RunContext, ModelRetry

from .talisman_config import TalismanConfig, get_config

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
    
    # Check if the gene looks like bacterial (common for Salmonella)
    bacterial_gene_patterns = ["inv", "sip", "sop", "sic", "spa", "ssa", "sse", "prg"]
    is_likely_bacterial = any(gene_id.lower().startswith(pattern) for pattern in bacterial_gene_patterns)
    
    # Default organisms to try based on gene patterns
    if is_likely_bacterial and not organism:
        organisms_to_try = ["Salmonella", "Escherichia coli", "Bacteria"]
    else:
        organisms_to_try = [organism] if organism else ["Homo sapiens", None]  # Try human first as default, then any organism
    
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
        # For bacterial genes, try organism-specific search first
        protein_ids = []
        if is_likely_bacterial:
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
        else:
            # Standard protein search (no organism constraint)
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
    
    # Check if this looks like a bacterial gene code
    bacterial_gene_patterns = ["inv", "sip", "sop", "sic", "spa", "ssa", "sse", "prg", "flh", "fli", "che"]
    is_likely_bacterial = any(gene_id.lower().startswith(pattern) for pattern in bacterial_gene_patterns)
    
    # Auto-detect organism based on gene pattern
    if is_likely_bacterial and not organism:
        logging.info(f"Gene {gene_id} matches bacterial pattern, setting organism to Salmonella")
        organism = "Salmonella"
    
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
        A structured biological summary of the gene set
    """
    logging.info(f"Starting gene set analysis for: {gene_list}")
    
    # Detect if these look like bacterial genes
    bacterial_gene_patterns = ["inv", "sip", "sop", "sic", "spa", "ssa", "sse", "prg", "flh", "fli", "che", "DVU"]
    gene_ids_list = parse_gene_list(gene_list)
    is_likely_bacterial = any(
        any(gene_id.lower().startswith(pattern) for pattern in bacterial_gene_patterns)
        for gene_id in gene_ids_list
    )
    
    # Set organism based on pattern detection
    organism = None
    if is_likely_bacterial:
        logging.info(f"Detected likely bacterial genes: {gene_list}")
        # Check for specific bacterial gene patterns
        if any(gene_id.lower().startswith(("inv", "sip", "sop", "sic", "spa")) for gene_id in gene_ids_list):
            organism = "Salmonella"
            logging.info(f"Setting organism to Salmonella based on gene patterns")
        elif any(gene_id.startswith("DVU") for gene_id in gene_ids_list):
            organism = "Desulfovibrio"
            logging.info(f"Setting organism to Desulfovibrio based on gene patterns")
    
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
    
    # Prepare a prompt for the LLM
    prompt = f"""Analyze the following set of genes and provide a detailed biological summary:

Gene IDs/Symbols: {', '.join(gene_ids)}

Gene Information:
{gene_descriptions}

{f"IMPORTANT: These genes are from {detected_organism or organism}. Make sure your analysis reflects the correct organism context." if detected_organism or organism else ""}

Based on this information, provide a structured analysis covering:
1. Shared biological processes these genes may participate in
2. Potential protein-protein interactions or functional relationships
3. Common cellular localization patterns
4. Involvement in similar pathways
5. Coordinated activities or cooperative functions
6. Any disease associations that multiple genes in this set share

Focus particularly on identifying relationships between at least a pair of these genes.
If the genes appear unrelated, note this but try to identify any subtle connections based on their function.

Your analysis should include multiple kinds of relationships:
- Functional relationships
- Pathway relationships
- Regulatory relationships
- Localization patterns
- Physical interactions
- Genetic interactions

Format the response with appropriate markdown headings and bullet points.

IMPORTANT: You MUST include ALL of the following sections in your response:

1. First provide your detailed analysis with appropriate headings for each section.

2. After your analysis, include a distinct section titled "## Terms" 
that contains a semicolon-delimited list of functional terms relevant to the gene set, 
ordered by relevance. These terms should include:
- Gene Ontology biological process terms (e.g., DNA repair, oxidative phosphorylation, signal transduction)
- Molecular function terms (e.g., kinase activity, DNA binding, transporter activity)
- Cellular component/localization terms (e.g., nucleus, plasma membrane, mitochondria)
- Pathway names (e.g., glycolysis, TCA cycle, MAPK signaling)
- Co-regulation terms (e.g., stress response regulon, heat shock response)
- Interaction networks (e.g., protein complex formation, signaling cascade)
- Metabolic process terms (e.g., fatty acid synthesis, amino acid metabolism)
- Regulatory mechanisms (e.g., transcriptional regulation, post-translational modification)
- Disease associations (if relevant, e.g., virulence, pathogenesis, antibiotic resistance)
- Structural and functional domains/motifs (e.g., helix-turn-helix, zinc finger)

Example of Terms section:
## Terms
DNA damage response; p53 signaling pathway; apoptosis; cell cycle regulation; tumor suppression; DNA repair; protein ubiquitination; transcriptional regulation; nuclear localization; cancer predisposition

3. After the Terms section, include a summary table of the genes analyzed titled "## Gene Summary Table"
Format it as a markdown table with the following columns in this exact order:
- ID: The gene identifier (same as Gene Symbol)
- Annotation: Genomic coordinates or accession with position information
- Genomic Context: Information about the genomic location (chromosome, plasmid, etc.)
- Organism: The organism the gene belongs to
- Description: The protein/gene function description

Make sure the information is accurate based on the gene information provided and do not conflate with similarly named genes from different organisms.

Example:

## Gene Summary Table
| ID | Annotation | Genomic Context | Organism | Description |
|-------------|-------------|----------|----------------|------------|
| BRCA1 | NC_000017.11 (43044295..43125483) | Chromosome 17 | Homo sapiens | Breast cancer type 1 susceptibility protein |
| TP53 | NC_000017.11 (7668402..7687550) | Chromosome 17 | Homo sapiens | Tumor suppressor protein |

For bacterial genes, the table should look like:

## Gene Summary Table
| ID | Annotation | Genomic Context | Organism | Description |
|-------------|-------------|----------|----------------|------------|
| invA | NC_003197.2 (3038407..3040471, complement) | Chromosome | Salmonella enterica | Invasion protein |
| DVUA0001 | NC_005863.1 (699..872, complement) | Plasmid pDV | Desulfovibrio vulgaris str. Hildenborough | Hypothetical protein |

REMEMBER: ALL THREE SECTIONS ARE REQUIRED - Main Analysis, Terms, and Gene Summary Table.
"""
    
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
        logging.info("Sending request to OpenAI API...")
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a biology expert analyzing gene sets to identify functional relationships. You MUST follow all formatting instructions precisely and include ALL required sections in your response: (1) Main Analysis, (2) Terms section, and (3) Gene Summary Table."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        logging.info("Received response from OpenAI API")
        
        # Extract the response content
        result = response.choices[0].message.content
        
        # Save the response to a timestamped file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"talisman_analysis_{timestamp}.json"
        
        # Create a directory for analysis results if it doesn't exist
        results_dir = os.path.join(os.path.expanduser("~"), "talisman_results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Save the full response including metadata
        file_path = os.path.join(results_dir, filename)
        logging.info(f"Saving analysis results to: {file_path}")
        
        with open(file_path, 'w') as f:
            # Create a dictionary with both the result and input/metadata
            output_data = {
                "timestamp": timestamp,
                "genes_analyzed": gene_ids,
                "model": model_name,
                "raw_response": response.model_dump(),
                "analysis_result": result
            }
            json.dump(output_data, f, indent=2)
            
        logging.info(f"Analysis complete. Results saved to: {file_path}")
        
        return result
    except Exception as e:
        logging.error(f"Error generating gene set analysis: {str(e)}")
        raise ModelRetry(f"Error generating gene set analysis: {str(e)}")