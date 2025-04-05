"""
Agent for reviewing GO standard annotations.
"""
from pydantic_ai import Agent, Tool, RunContext

from aurelian.agents.goann.goann_config import GOAnnotationDependencies
from aurelian.utils.documentation_manager import DocumentationManager
from aurelian.agents.literature.literature_tools import (
    lookup_pmid as literature_lookup_pmid,
    search_literature_web,
    retrieve_literature_page
)
from . import DOCUMENTS_DIR
from .goann_tools import find_gene_annotations, fetch_document
from ..uniprot import lookup_uniprot_entry

SYSTEM = """
You are a GO annotation reviewer specializing in reviewing GO standard annotations.

Your primary responsibilities include:
1. Evaluating GO annotations for accuracy based on evidence codes and supporting literature
2. Identifying potential over-annotations based on phenotypes rather than direct involvement
3. Reviewing annotations according to GO annotation guidelines
4. Suggesting corrections or improvements to annotations

You use the GO guidelines for proper annotation, you can use the `fetch_document` tool to retrieve the content of any of these documents.

A gene should only be annotated to a process if its activity is an identifiable step in that process.

When asked to evaluate or review existing annotations, be sure to:

- check the papers used in annotation using `literature_lookup_pmid` to ensure the interpretation of the evidence is correct
- look at textual information on the uniprot ID usingg `lookup_uniprot_entry` to ensure the annotation is consistent


Your goal is to help maintain the quality and accuracy of the GO annotation database.
"""

# Define core tools for the agent
core_tools = [
    Tool(find_gene_annotations),
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
]

# Create the GO annotation review agent
goann_agent = Agent(
    model="anthropic:claude-3-7-sonnet-latest",
    deps_type=GOAnnotationDependencies,
    system_prompt=SYSTEM,
    tools=core_tools,
)


def get_documents_for_prompt() -> str:
    """
    Get the documents for the system prompt.

    Returns:
        A string containing the list of available GO annotation best practice documents
    """
    dm = DocumentationManager(documents_dir=DOCUMENTS_DIR)
    return dm.get_documents_for_prompt(extra_text=(
        "\n\nYou can use the `fetch_document` tool to retrieve the content of any of these documents."
        "\nWhen asked any question about GO annotation curation practice, be sure to ALWAYS"
        " check the relevant document for the most up-to-date information.\n"
    ))


@goann_agent.system_prompt
def add_documents_to_prompt(ctx: RunContext[GOAnnotationDependencies]) -> str:
    """
    Add available GO-CAM documents to the system prompt.
    
    Args:
        ctx: The run context
        
    Returns:
        A string containing the list of available GO-CAM documents
    """
    return get_documents_for_prompt()
