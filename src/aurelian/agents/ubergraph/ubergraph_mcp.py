"""
MCP tools for working with ontologies via UberGraph endpoint.
"""
import os
from typing import Dict, Optional

from mcp.server.fastmcp import FastMCP

import aurelian.agents.ubergraph.ubergraph_tools as ut
from aurelian.agents.ubergraph.ubergraph_config import Dependencies, get_config
from pydantic_ai import RunContext

# Initialize FastMCP server with combined system prompt
SYSTEM_PROMPT = """
You are an expert ontologist with access to the UberGraph SPARQL endpoint.

UberGraph is a knowledge graph built from multiple OBO ontologies, including GO, Uberon, CL, ChEBI, and more.
You can help users explore ontology terms, relationships, and hierarchies through SPARQL queries.

IMPORTANT ASSUMPTIONS:
- When formulating your response to tool outputs, you can extemporize with your own knowledge,
  but if you do so, you must be clear about which statements come from the ontology vs your own knowledge.
- Include both IDs and labels in responses, unless directed not to do so.
- Assume OBO style ontology and OBO PURLs (http://purl.obolibrary.org/obo/).
- All edges are stored as simple triples, e.g CL:0000080 BFO:0000050 UBERON:0000179 for 'circulating cell'
  'part of' 'haemolymphatic fluid'
- Direct (asserted) edges are stored in the 'renci:ontology' graph. Use this by default, even for subClassOf.
- Indirect (entailed) edges (including reflexive) are stored in the 'renci:redundant' graph. Use this for
  queries that require transitive closure, e.g. rdfs:subClassOf+
"""

mcp = FastMCP("ubergraph", instructions=SYSTEM_PROMPT)


from aurelian.dependencies.workdir import WorkDir

def deps() -> Dependencies:
    deps = get_config()
    # Set the location from environment variable or default
    loc = os.getenv("AURELIAN_WORKDIR", "/tmp/aurelian")
    deps.workdir = WorkDir(loc)
    return deps

def ctx() -> RunContext[Dependencies]:
    rc: RunContext[Dependencies] = RunContext[Dependencies](
        deps=deps(),
        model=None, usage=None, prompt=None,
    )
    return rc


@mcp.tool()
async def query_ubergraph(query: str, format: Optional[str] = "text") -> Dict:
    """
    Execute a SPARQL query against the UberGraph endpoint.
    
    Args:
        query: The SPARQL query to execute
        format: Output format (text or json)
        
    Returns:
        The query results
    """
    return await ut.query_ubergraph(ctx(), query, format)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')