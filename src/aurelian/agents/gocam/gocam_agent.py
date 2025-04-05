"""
Agent for working with GO-CAMs (Gene Ontology Causal Activity Models).
"""
from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel, Field

from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from aurelian.agents.gocam.gocam_tools import (
    search_gocams,
    lookup_gocam,
    lookup_uniprot_entry,
    all_documents,
    fetch_document,
    lookup_gocam_local,
)
from aurelian.agents.literature.literature_tools import (
    lookup_pmid as literature_lookup_pmid,
    search_literature_web,
    retrieve_literature_page
)
from aurelian.agents.filesystem.filesystem_tools import inspect_file, list_files
from pydantic_ai import Agent, Tool, RunContext

class RecommendationStrength(str, Enum):
    """
    Enum for recommendation strength.
    """
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"

class Recommendation(BaseModel):
    """
    Recommendation for improving a GO-CAM model.
    """
    text: str
    strength: RecommendationStrength

    class Config:
        schema_extra = {
            "example": {
                "text": "Improve the clarity of the model diagram.",
                "strength": RecommendationStrength.MAJOR
            }
        }

class GOCamReviewSummary(BaseModel):
    """
    Summary of the review of a GO-CAM model with rubric scores.
    """
    model_id: str
    model_title: str
    taxa: Optional[List[str]] = Field(description="List of taxa (formal scientific names)")
    genes: Optional[List[str]] = Field(description="List of genes in the model")
    model_description: str = Field(description="Description of the model")
    review_summary: str = Field(description="Brief summary of the review")
    best_practice_score: Optional[int] = Field(None, description="Score 1-5 for adherence to GO-CAM best practices", ge=1, le=5)
    specific_best_practice_scores: Optional[Dict[str, int]] = Field(None, description="Key-value set of scores for each relevant best practice. Each key is the name of a specific best practice (use the document name), and the value is the score 1-5. Only for relevant best practices")
    biological_content_score: Optional[int] = Field(None, description="Score 1-5 for accuracy of biological content against literature", ge=1, le=5)
    publication_consistency_score: Optional[int] = Field(None, description="Score 1-5 for consistency with publications", ge=1, le=5)
    uniprot_consistency_score: Optional[int] = Field(None, description="Score 1-5 for consistency with uniprot information", ge=1, le=5)
    causal_connections_score: Optional[int] = Field(None, description="Score 1-5 for logical connection of activities in pathway flow", ge=1, le=5)
    simplicity_score: Optional[int] = Field(None, description="Score 1-5 for model parsimony and human understandability", ge=1, le=5)
    completeness_score: Optional[int] = Field(None, description="Score 1-5 for model completeness", ge=1, le=5)
    overall_score: Optional[int] = Field(None, description="Overall score 1-5 for the model", ge=1, le=5)
    recommendations: Optional[List[Recommendation]] = Field(None, description="Key recommendations for improvement, highest priority first")


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
- RO:0002307 *indirectly positively regulates*
- RO:0002308 *indirectly negatively regulates*

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

For each review, you should score the model on a scale of 1-5 (5 being best) for each of these criteria:
1. Best Practices: adherence to GO-CAM best practices
2. Biological Content: accuracy of biological content against literature
3. Protein Consistency: consistency with known protein functions and interactions
4. Causal Connections: logical connection of activities in pathway flow
5. Parsimony: model simplicity and human understandability

Provide an overall score (1-5) and key recommendations for improvement at the end of your review.
If any criteria are not applicable, mark them as N/A.

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


REVIEW_SUMMARIZER_SYSTEM = """Your job is to summarize the existing review of a GO-CAM model, completing
the rubric for all of the criteria.
"""

gocam_review_summarizer_agent = Agent(
    model="anthropic:claude-3-7-sonnet-latest",
    deps_type=GOCAMDependencies,
    system_prompt=REVIEW_SUMMARIZER_SYSTEM,
    tools=[
        #Tool(lookup_gocam_local),
    ],
    result_type=GOCamReviewSummary,
)