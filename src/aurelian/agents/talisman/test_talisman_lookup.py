#!/usr/bin/env python3
"""
Test script for Talisman protein lookup functionality using NCBI EUtils directly.
This script tests the lookup of protein information using the 8YJT_C2 example.
"""

import sys
from bioservices.eutils import EUtils as NCBI

def test_protein_lookup(protein_id):
    """Test protein lookup using NCBI EUtils directly.
    
    Args:
        protein_id: The protein ID to look up
        
    Returns:
        The protein information
    """
    ncbi = NCBI(email="talisman_agent@aurelian.app")
    
    print(f"Talisman Agent - Looking up protein: {protein_id}")
    
    # Search for the protein ID
    search_results = ncbi.ESearch("protein", protein_id)
    protein_ids = search_results.get('idlist', [])
    
    if not protein_ids:
        print(f"No protein found with ID: {protein_id}")
        return None
    
    print(f"Found protein IDs: {protein_ids}")
    protein_id = protein_ids[0]
    
    # Get protein sequence
    print(f"Fetching protein sequence for ID: {protein_id}")
    protein_data = ncbi.EFetch("protein", id=protein_id, rettype="fasta", retmode="text")
    
    # Get protein summary
    print("Fetching protein summary")
    summary_data = ncbi.ESummary("protein", id=protein_id)
    
    # Extract and format useful summary information
    if isinstance(summary_data, dict) and summary_data:
        print("Summary data:")
        for key, value in summary_data.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"  {k}: {v}")
    
    return f"Protein Sequence:\n{protein_data}"

if __name__ == "__main__":
    protein_id = "8YJT_C2"
    if len(sys.argv) > 1:
        protein_id = sys.argv[1]
    
    print("Talisman Agent Protein Lookup Test")
    print("==================================")
    result = test_protein_lookup(protein_id)
    if result:
        print("\nResult:\n")
        print(result)