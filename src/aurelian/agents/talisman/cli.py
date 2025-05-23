"""
CLI interface for the talisman agent.
This may not be in the original code, but let's add it to make sure it's properly configured.
"""
import logging
import re
from pydantic_ai import RunContext

from aurelian.agents.talisman.talisman_config import TalismanConfig
from aurelian.agents.talisman.talisman_tools import GeneSetAnalysis, FunctionalTerm, GeneSummary

def format_talisman_output(result):
    """Format the talisman output to ensure it always has all three sections."""
    logging.info("Post-processing talisman output")
    
    # Check if output already has proper sections
    has_narrative = re.search(r'^\s*##\s*Narrative', result, re.MULTILINE) is not None
    has_functional_terms = re.search(r'^\s*##\s*Functional Terms Table', result, re.MULTILINE) is not None
    has_gene_summary = re.search(r'^\s*##\s*Gene Summary Table', result, re.MULTILINE) is not None
    
    # If all sections are present, return as is
    if has_narrative and has_functional_terms and has_gene_summary:
        return result
    
    # Need to reconstruct the output
    # Extract gene summary table if it exists
    gene_table_match = re.search(r'^\s*##\s*Gene Summary Table\s*\n(.*?)(?=$|\n\n|\Z)', 
                                result, re.MULTILINE | re.DOTALL)
    
    if gene_table_match:
        gene_table = gene_table_match.group(0)
        
        # Extract existing text that might be a narrative
        narrative_text = result.replace(gene_table, '').strip()
        
        # Create a proper narrative section if missing
        if not has_narrative and narrative_text:
            narrative_section = "## Narrative\n" + narrative_text + "\n\n"
        else:
            narrative_section = "## Narrative\nThese genes may have related functions as indicated in the gene summary table.\n\n"
        
        # Create a functional terms section if missing
        if not has_functional_terms:
            # Extract gene IDs from the gene table
            gene_ids = []
            for line in gene_table.split('\n'):
                if '|' in line and not line.strip().startswith('|--') and not 'ID |' in line:
                    parts = line.split('|')
                    if len(parts) > 1:
                        gene_id = parts[1].strip()
                        if gene_id and gene_id != 'ID':
                            gene_ids.append(gene_id)
            
            # Create a simple functional terms table
            functional_terms = "## Functional Terms Table\n"
            functional_terms += "| Functional Term | Genes | Source |\n"
            functional_terms += "|-----------------|-------|--------|\n"
            functional_terms += f"| Gene set | {', '.join(gene_ids)} | Analysis |\n\n"
        else:
            # Find and extract existing functional terms section
            ft_match = re.search(r'^\s*##\s*Functional Terms Table\s*\n(.*?)(?=^\s*##\s*|\Z)', 
                                result, re.MULTILINE | re.DOTALL)
            functional_terms = ft_match.group(0) if ft_match else ""
        
        # Reconstruct the output with all sections
        formatted_output = "# Gene Set Analysis\n\n" + narrative_section + functional_terms + gene_table
        return formatted_output
    
    # If no gene table was found, return the original result
    return result