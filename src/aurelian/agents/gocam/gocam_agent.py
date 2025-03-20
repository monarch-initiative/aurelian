"""
Agent for working with GO-CAMs (Gene Ontology Causal Activity Models).
"""
from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from aurelian.agents.gocam.gocam_tools import (
    search_gocams,
    lookup_gocam,
    lookup_uniprot_entry,
    all_documents,
    fetch_document,
    validate_gocam_model, lookup_gocam_local,
)
from aurelian.agents.literature.literature_tools import (
    lookup_pmid as literature_lookup_pmid,
    search_literature_web,
    retrieve_literature_page
)
from aurelian.agents.filesystem.filesystem_tools import inspect_file, list_files
from pydantic_ai import Agent, Tool, RunContext

SYSTEM_CURIES = """
When providing results in markdown, you should generally include CURIEs/IDs, and you can 
hyperlink these as https://bioregistry.io/{curie}. Note that GO-CAM IDs should be hyperlinked 
as https://bioregistry.io/go.model:{uuid}."""

PREDICATES_INFO = """
The following predicates are used for causal associations:

- RO:0002413 *provides input for*
- RO:0002629 *directly positively regulates*
- RO:0002630 *directly negatively regulates*
- RO:0002304 *causally upstream of, positive effect*
- RO:0002305 *causally upstream of, negative effect*

"""

SYSTEM = f"""
You are an expert molecular biologist with access to the GO-CAM database.

GO-CAMs (Gene Ontology Causal Activity Models) are standardized models that represent 
biological processes and pathways, including gene functions and interactions.

You can help with:
- Searching for GO-CAM models by pathway, gene, or complex queries
- Looking up specific GO-CAM models by ID
- Finding information about proteins via UniProt
- Analyzing and comparing biological pathways
- Retrieving literature related to GO-CAMs via PubMed
- Retrieving GO-CAM annotation best practice documents
- Validating GO-CAM model structure against the schema

You can provide information on gene functions, pathways, and models. When giving your response, 
stick to communicating the information provided in the response. You may extemporize and fill 
in gaps with your own knowledge, but always be clear about what information came from the call 
vs your own knowledge.

{PREDICATES_INFO}

{SYSTEM_CURIES}
"""

core_tools = [
    Tool(search_gocams),
    Tool(lookup_gocam),
    Tool(lookup_uniprot_entry),
    Tool(literature_lookup_pmid,
         description="""Lookup the text of a PubMed article by its PMID.

                        Note that assertions in GO-CAMs may reference PMIDs, so this tool
                        is useful for validating assertions. A common task is to align
                        the text of a PMID with the text of an assertion, or extracting text
                        snippets from the publication that support the assertion."""),
    Tool(search_literature_web),
    Tool(retrieve_literature_page),
    Tool(fetch_document),
    Tool(inspect_file),
    Tool(list_files),
]


gocam_agent = Agent(
    model="openai:gpt-4o",
    deps_type=GOCAMDependencies,
    system_prompt=SYSTEM,
    tools=core_tools,
)

def get_documents_for_prompt() -> str:
    """
    Get the documents for the system prompt.

    Returns:
        A string containing the list of available GO-CAM documents
    """
    meta = all_documents()
    if not meta["documents"]:
        return "\nNo GO-CAM best practice documents are available."

    docs_text = "\n\nThe following GO-CAM best practice documents are available:\n"
    docs_text += "\n".join([f"- {d['title']}" for d in meta["documents"]])
    docs_text += "\n\nYou can use the `fetch_document` tool to retrieve the content of any of these documents."
    docs_text += "\nWhen asked any question about GO-CAM curation practice, be sure to ALWAYS"
    docs_text += " check the relevant document for the most up-to-date information.\n"
    docs_text += "Some of these docs refer to particular exemplar models. these can be retrieved with the `lookup_gocam` tool."
    return docs_text

@gocam_agent.system_prompt
def add_documents(ctx: RunContext[GOCAMDependencies]) -> str:
    """
    Add available GO-CAM documents to the system prompt.
    
    Args:
        ctx: The run context
        
    Returns:
        A string containing the list of available GO-CAM documents
    """
    return get_documents_for_prompt()


REVIEWER_SYSTEM = f"""
You are a GO-CAM curator in charge of reviewing proposed GO-CAMs.

GO-CAMs (Gene Ontology Causal Activity Models) are standardized models that represent 
biological processes and pathways, including gene functions and interactions.

Your job is to examine proposed models, and to perform review and QC, including:

- checking that the model is consistent with all relevant GO-CAM best practices (see `fetch_document`)
- ensuring the biological content of the model is consistent with the literature and textbook knowledge (see `literature_lookup_pmid`)
- everything is consistent with what is known about that protein (see `lookup_uniprot_entry`)
- activities in the model are connected in a way that is consistent with the activity flow in the pathway
- the model is parsimonious and easy for a human to understand

{PREDICATES_INFO}

{SYSTEM_CURIES}
"""

gocam_reviewer_agent = Agent(
    model="anthropic:claude-3-7-sonnet-latest",
    deps_type=GOCAMDependencies,
    system_prompt=REVIEWER_SYSTEM,
    tools=[
        *core_tools,
        Tool(lookup_gocam_local),
        #Tool(validate_gocam_model),
    ],
)


@gocam_reviewer_agent.system_prompt
def add_documents(ctx: RunContext[GOCAMDependencies]) -> str:
    """
    Add available GO-CAM documents to the system prompt.

    Args:
        ctx: The run context

    Returns:
        A string containing the list of available GO-CAM documents
    """
    return get_documents_for_prompt()