#!/usr/bin/env python3
"""
Test script for Talisman protein lookup functionality using NCBI EUtils.
This script tests the lookup of protein information using mock data.
"""

import pytest
from unittest.mock import patch, MagicMock

from aurelian.agents.talisman.talisman_config import TalismanConfig, get_config
from aurelian.agents.talisman.talisman_tools import get_ncbi_gene_info


@pytest.fixture
def mock_ncbi():
    """Create a mock NCBI client."""
    mock = MagicMock()
    
    # Configure ESearch to return a mock ID list
    mock.ESearch.return_value = {"idlist": ["12345"]}
    
    # Configure EFetch to return mock protein data
    mock.EFetch.return_value = """>NP_000537.3 tumor protein p53 [Homo sapiens]
MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD
"""
    
    # Configure ESummary to return mock summary data
    mock.ESummary.return_value = {
        "12345": {
            "title": "tumor protein p53 [Homo sapiens]",
            "organism": "Homo sapiens",
            "accessionversion": "NP_000537.3"
        }
    }
    
    return mock


def test_protein_lookup(mock_ncbi):
    """Test protein lookup using a mock NCBI client."""
    with patch('aurelian.agents.talisman.talisman_config.TalismanConfig.get_ncbi_client', 
               return_value=mock_ncbi):
        
        # Create a mock context
        mock_ctx = MagicMock()
        mock_ctx.deps = get_config()
        
        # Test with a protein ID
        result = get_ncbi_gene_info(mock_ctx, "TP53")
        
        # Verify result
        assert result is not None
        assert "tumor protein p53" in result
        assert "Homo sapiens" in result
        
        # Verify that the correct methods were called
        mock_ncbi.ESearch.assert_called()
        mock_ncbi.EFetch.assert_called()
        mock_ncbi.ESummary.assert_called()