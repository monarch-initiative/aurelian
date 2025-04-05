#!/usr/bin/env python3
"""
Simplified test script for the gene analysis functionality.
"""

import os
import sys
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
        uniprot_info = u.search(f'gene:{gene_id} OR accession:{gene_id} OR id:{gene_id}', 
                               frmt="tsv", columns="accession,id,gene_names,organism,protein_name,function")
        if uniprot_info and uniprot_info.strip() != "":
            print(f"Found information in UniProt")
            return f"UniProt Information:\n{uniprot_info}"
    except Exception as e:
        print(f"Error querying UniProt: {str(e)}")
    
    # Fall back to NCBI
    try:
        ncbi = NCBI(email="gene_agent@aurelian.app")
        
        # Try gene database
        search_results = ncbi.ESearch("gene", gene_id)
        gene_ids = search_results.get('idlist', [])
        
        if gene_ids:
            gene_id = gene_ids[0]
            gene_data = ncbi.EFetch("gene", id=gene_id)
            return f"NCBI Gene Information:\n{gene_data}"
            
        # Try protein database
        search_results = ncbi.ESearch("protein", gene_id)
        protein_ids = search_results.get('idlist', [])
        
        if protein_ids:
            protein_id = protein_ids[0]
            protein_data = ncbi.EFetch("protein", id=protein_id, rettype="fasta", retmode="text")
            
            # Get additional details with esummary
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
"""
    
    print("Generating biological analysis...")
    
    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a biology expert analyzing gene sets to identify functional relationships."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
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