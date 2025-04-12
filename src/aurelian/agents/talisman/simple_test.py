#!/usr/bin/env python3
"""
Simplified test script for the gene analysis functionality.
"""

import os
import sys
import time
import openai

from bioservices import UniProt
from bioservices.eutils import EUtils as NCBI

# Ensure the OpenAI API key is set
if "OPENAI_API_KEY" not in os.environ:
    print("Warning: OPENAI_API_KEY environment variable not set.")
    print("Set your API key with: export OPENAI_API_KEY=your_key_here")
    sys.exit(1)

openai.api_key = os.environ["OPENAI_API_KEY"]

def get_gene_info(gene_id):
    """Get information about a gene from UniProt and NCBI."""
    print(f"Looking up information for gene: {gene_id}")
    
    # Try UniProt first
    try:
        u = UniProt(verbose=False)
        # Rate limit to max 3 requests per second
        time.sleep(0.34)
        uniprot_info = u.search(f'gene:{gene_id} OR accession:{gene_id} OR id:{gene_id}', 
                               frmt="tsv", columns="accession,id,gene_names,organism,protein_name,function")
        if uniprot_info and uniprot_info.strip() != "":
            print(f"Found information in UniProt")
            return f"UniProt Information:\n{uniprot_info}"
    except Exception as e:
        print(f"Error querying UniProt: {str(e)}")
    
    # Fall back to NCBI
    try:
        ncbi = NCBI(email="MJoachimiak@lbl.gov")
        
        # Try gene database
        time.sleep(0.34)  # Rate limit to max 3 requests per second
        search_results = ncbi.ESearch("gene", gene_id)
        gene_ids = search_results.get('idlist', [])
        
        if gene_ids:
            gene_id = gene_ids[0]
            time.sleep(0.34)  # Rate limit to max 3 requests per second
            gene_data = ncbi.EFetch("gene", id=gene_id)
            return f"NCBI Gene Information:\n{gene_data}"
            
        # Try protein database
        time.sleep(0.34)  # Rate limit to max 3 requests per second
        search_results = ncbi.ESearch("protein", gene_id)
        protein_ids = search_results.get('idlist', [])
        
        if protein_ids:
            protein_id = protein_ids[0]
            time.sleep(0.34)  # Rate limit to max 3 requests per second
            protein_data = ncbi.EFetch("protein", id=protein_id, rettype="fasta", retmode="text")
            
            # Get additional details with esummary
            time.sleep(0.34)  # Rate limit to max 3 requests per second
            summary_data = ncbi.ESummary("protein", id=protein_id)
            
            if isinstance(summary_data, dict) and summary_data:
                title = None
                organism = None
                
                for key, value in summary_data.items():
                    if isinstance(value, dict):
                        if 'title' in value:
                            title = value['title']
                        if 'organism' in value:
                            organism = value['organism']
                
                if title or organism:
                    protein_data = f"Title: {title or 'Not available'}\nOrganism: {organism or 'Unknown'}\n\n{protein_data}"
            
            return f"NCBI Protein Information:\n{protein_data}"
        
        return "No information found for this gene ID."
    except Exception as e:
        print(f"Error querying NCBI: {str(e)}")
        return "Error retrieving gene information."

def analyze_gene_set(gene_list):
    """Analyze a set of genes and generate a biological summary."""
    # Parse gene list
    if isinstance(gene_list, str):
        genes = [g.strip() for g in gene_list.replace(',', ' ').replace(';', ' ').split() if g.strip()]
    else:
        genes = gene_list
    
    print(f"Analyzing genes: {', '.join(genes)}")
    
    # Get information for each gene
    gene_info = {}
    for gene in genes:
        info = get_gene_info(gene)
        gene_info[gene] = info
        print(f"Retrieved information for {gene}")
    
    # Prepare the prompt for OpenAI
    prompt = f"""Analyze the following set of genes and provide a detailed biological summary:

Gene IDs/Symbols: {', '.join(genes)}

Gene Information:
"""
    
    for gene, info in gene_info.items():
        prompt += f"\n## Gene: {gene}\n{info}\n"
    
    prompt += """
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
Format it as a markdown table with columns for Gene Symbol and brief description from the gene information.
Make sure the descriptions are accurate based on the gene information provided and do not conflate with similarly named genes from different organisms.

REMEMBER: ALL THREE SECTIONS ARE REQUIRED - Main Analysis, Terms, and Gene Summary Table.
"""
    
    print("Generating biological analysis...")
    
    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a biology expert analyzing gene sets to identify functional relationships. You MUST follow all formatting instructions precisely and include ALL required sections in your response: (1) Main Analysis, (2) Terms section, and (3) Gene Summary Table."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        analysis = response.choices[0].message.content
        return analysis
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

if __name__ == "__main__":
    # Default gene set for testing - TP53 and MDM2 (well-known interaction)
    default_gene_list = "TP53, MDM2"
    
    gene_list = default_gene_list
    if len(sys.argv) > 1:
        gene_list = sys.argv[1]
    
    result = analyze_gene_set(gene_list)
    if result:
        print("\nGene Set Analysis:\n")
        print(result)