from pydantic_ai import Agent, Tool, RunContext

from aurelian.agents.gocam import GOCAMDependencies, validate_gocam_model
from aurelian.agents.gocam.gocam_agent import PREDICATES_INFO, SYSTEM_CURIES, core_tools, \
    get_documents_for_prompt
from aurelian.agents.gocam.gocam_tools import lookup_gocam_local

CURATOR_SYSTEM = f"""
You are a GO-CAM curator in charge of curating GO-CAMs.

When curating a GO-CAM, you should first review all relevant information:

- read the relevant papers provided to you `literature_lookup_pmid`
- find any additional references or papers of relevance `lookup_uniprot_entry`
- check the relevant GO-CAM best practices (see `fetch_document`)
- find the right uniprot IDs, and check what information is known `lookup_uniprot_entry`
- find the relevant GO and ontology terms `lookup_go_term`

{PREDICATES_INFO}

{SYSTEM_CURIES}
"""
gocam_curator_agent = Agent(
    model="anthropic:claude-3-7-sonnet-latest",
    deps_type=GOCAMDependencies,
    system_prompt=CURATOR_SYSTEM,
    tools=[
        *core_tools,
        Tool(lookup_gocam_local),
        Tool(validate_gocam_model),
    ],
)


@gocam_curator_agent.system_prompt
def add_documents(ctx: RunContext[GOCAMDependencies]) -> str:
    """
    Add available GO-CAM documents to the system prompt.

    Args:
        ctx: The run context

    Returns:
        A string containing the list of available GO-CAM documents
    """
    return get_documents_for_prompt()
