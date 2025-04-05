"""
Tools for the GO Annotation Review agent.
"""
from typing import List, Dict, Optional

from pydantic_ai import RunContext, ModelRetry

from aurelian.agents.goann.goann_config import GOAnnotationDependencies
from aurelian.utils.data_utils import obj_to_dict

from . import DOCUMENTS_DIR
from ...utils.documentation_manager import DocumentationManager

document_manager = DocumentationManager(documents_dir=DOCUMENTS_DIR)

async def find_gene_annotations(ctx: RunContext[GOAnnotationDependencies], gene_id: str) -> List[Dict]:
    """
    Find gene annotations for a given gene or gene product.
    
    Args:
        ctx: The run context
        gene_id: Gene or gene product IDs. This should be a prefixed ID, consistent with AmiGO
        
    Returns:
        List[Dict]: List of gene annotations including their evidence codes
    """
    print(f"FIND GENE ANNOTATIONS: {gene_id}")
    try:
        adapter = ctx.deps.get_amigo_adapter()
        normalized_gene_id = ctx.deps.get_gene_id(gene_id)
        assocs = [obj_to_dict(a) for a in adapter.associations([normalized_gene_id])]
        
        if not assocs:
            raise ModelRetry(f"No gene annotations found for {gene_id}. Try a different gene identifier.")
            
        return assocs
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error finding gene annotations for {gene_id}: {str(e)}")


async def fetch_document(
        ctx: RunContext[GOAnnotationDependencies],
        name: str,
        format: str = "md"
) -> str:
    """
    Lookup thedocument by name.

    Args:
        ctx: The run context
        name: The document name (e.g. "How_to_annotate_TFs")
        format: The format of the document (defaults to "md")

    Returns:
        The content of the document
    """
    print(f"FETCH DOCUMENT: {name}")
    try:
        return document_manager.fetch_document(name)
    except KeyError:
        raise ModelRetry(f"Document with name '{name}' not found. Please check the name and try again.")


