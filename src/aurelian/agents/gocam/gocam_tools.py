"""
Tools for the GOCAM agent.
"""
import os
import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Union, Any

from linkml_store.utils.format_utils import load_objects
from pydantic_ai import RunContext, ModelRetry
from pydantic import ValidationError

from gocam.datamodel.gocam import Model as GocamModel

from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from aurelian.agents.uniprot.uniprot_tools import normalize_uniprot_id
from aurelian.utils.data_utils import flatten
from aurelian.agents.literature.literature_tools import search_literature_web, retrieve_literature_page
from . import DOCUMENTS_DIR


async def search_gocams(ctx: RunContext[GOCAMDependencies], query: str) -> List[Dict]:
    """
    Performs a retrieval search over the GO-CAM database.

    The query can be any text, such as name of a pathway, genes, or
    a complex sentence.

    The objects returned are summaries of GO-CAM models; they do not contain full
    details. Use `lookup_gocam` to retrieve full details of a model.

    This tool uses a retrieval method that is not guaranteed to always return
    complete results, and some results may be less relevant than others.
    You MAY use your judgment in filtering these.

    Args:
        ctx: The run context
        query: The search query text

    Returns:
        List[Dict]: List of GOCAM models matching the query
    """
    print(f"SEARCH GOCAMS: {query}")
    try:
        qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
        objs = []
        for score, row in qr.ranked_rows:
            obj = flatten(row)
            obj["relevancy_score"] = score
            objs.append(obj)
            print(f"RESULT: {obj}")

        if not objs:
            raise ModelRetry(f"No GOCAM models found matching the query: {query}. Try a different search term.")

        return objs
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching GOCAM models: {str(e)}")


async def lookup_gocam_local(ctx: RunContext[GOCAMDependencies], path: str) -> Dict:
    """
    Performs a lookup of a GO-CAM model by its local file path.

    Args:
        ctx: The run context
        path: The local file path of the GO-CAM model
    """
    print(f"LOOKUP GOCAM LOCAL: {path}")
    try:
        path = Path(path)
        if not path.exists():
            raise ModelRetry(f"File not found: {path}")
        objects = load_objects(path)
        if not objects:
            raise ModelRetry(f"No objects found in file: {path}")
        if not isinstance(objects, list):
            objects = [objects]
        if len(objects) > 1:
            raise ModelRetry(f"Multiple objects found in file: {path}")
        if not isinstance(objects[0], dict):
            raise ModelRetry(f"Object is not a dictionary: {path}")
        return objects[0]
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error looking up GO-CAM model: {str(e)}")

async def lookup_gocam(ctx: RunContext[GOCAMDependencies], model_id: str) -> Dict:
    """
    Performs a lookup of a GO-CAM model by its ID, and returns the model.

    Args:
        ctx: The run context
        model_id: The ID of the GO-CAM model to look up

    Returns:
        Dict: The GO-CAM model data
    """
    print(f"LOOKUP GOCAM: {model_id}")
    try:
        # Normalize the model ID
        if ":" in model_id:
            parts = model_id.split(":")
            if parts[0] != "gomodel":
                model_id = f"gomodel:{parts[1]}"
        else:
            model_id = f"gomodel:{model_id}"

        qr = ctx.deps.collection.find({"id": model_id})
        if not qr.rows:
            raise ModelRetry(f"Could not find GO-CAM model with ID {model_id}. The ID may be incorrect.")
        return qr.rows[0]
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error looking up GO-CAM model {model_id}: {str(e)}")


async def lookup_uniprot_entry(ctx: RunContext[GOCAMDependencies], uniprot_acc: str) -> str:
    """
    Lookup the Uniprot entry for a given Uniprot accession number.

    This can be used to obtain further information about a protein in
    a GO-CAM.

    Args:
        ctx: The run context
        uniprot_acc: The Uniprot accession

    Returns:
        str: Detailed functional and other info about the protein
    """
    print(f"LOOKUP UNIPROT: {uniprot_acc}")
    try:
        normalized_acc = normalize_uniprot_id(uniprot_acc)
        uniprot_service = ctx.deps.get_uniprot_service()
        result = uniprot_service.retrieve(normalized_acc, frmt="txt")

        if not result or "Error" in result or "Entry not found" in result:
            raise ModelRetry(f"Could not find UniProt entry for {uniprot_acc}. The accession may be incorrect.")

        return result
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving UniProt entry for {uniprot_acc}: {str(e)}")


# These functions have been removed and replaced with direct use of
# literature_lookup_pmid, search_literature_web, and retrieve_literature_page
# from aurelian.agents.literature.literature_tools


def all_documents() -> Dict:
    """
    Get all available GO-CAM documentation.
    
    Returns:
        Dictionary of all available GO-CAM documents
    """
    if not DOCUMENTS_DIR.exists():
        return {"documents": []}
    
    documents = []
    for file_path in DOCUMENTS_DIR.glob("*.md"):
        doc_id = file_path.stem
        title = doc_id.replace("_", " ")
        documents.append({
            "id": doc_id,
            "title": title,
            "path": str(file_path)
        })
    
    return {"documents": documents}


async def fetch_document(
    ctx: RunContext[GOCAMDependencies], 
    name: str,
    format: str = "md"
) -> str:
    """
    Lookup the GO-CAM document by name.

    Args:
        ctx: The run context
        name: The document name (e.g. "How_to_annotate_complexes_in_GO-CAM")
        format: The format of the document (defaults to "md")
    
    Returns:
        The content of the document
    """
    print(f"FETCH DOCUMENT: {name}")
    try:
        # Get all available documents
        all_docs = all_documents()
        
        # Normalize document name and find it
        selected_document = None
        name_normalized = name.replace(" ", "_").lower()
        
        for document in all_docs["documents"]:
            if document["id"].lower() == name_normalized:
                selected_document = document
                break
            if document["title"].lower() == name.lower():
                selected_document = document
                break
                
        if not selected_document:
            available_docs = ", ".join([d["title"] for d in all_docs["documents"]])
            raise ModelRetry(
                f"Could not find document with name '{name}'. "
                f"Available documents: {available_docs}"
            )
            
        # Get the document file
        path = Path(selected_document["path"])
        
        if not path.exists():
            raise ModelRetry(f"Document file not found: {path}")
            
        # Read the document file
        with open(path) as f:
            content = f.read()
            
        if not content or content.strip() == "":
            raise ModelRetry(f"Document file is empty: {path}")
            
        return content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error fetching document: {str(e)}")


async def validate_gocam_model(
    ctx: RunContext[GOCAMDependencies],
    model_data: Union[str, Dict[str, Any]],
    format: str = "json"
) -> Dict[str, Any]:
    """
    Validate a GO-CAM model against the pydantic schema.
    
    Args:
        ctx: The run context
        model_data: The model data as a JSON/YAML string or dict
        format: The format of the input data (json or yaml)
    
    Returns:
        Dict with validation results, including success status and errors if any
    """
    try:
        # Parse the input data if it's a string
        if isinstance(model_data, str):
            if format.lower() == "json":
                parsed_data = json.loads(model_data)
            elif format.lower() == "yaml":
                parsed_data = yaml.safe_load(model_data)
            else:
                raise ModelRetry(f"Unsupported format: {format}. Must be 'json' or 'yaml'")
        else:
            parsed_data = model_data
        
        # Validate the model
        try:
            gocam_model = GocamModel(**parsed_data)
            return {
                "valid": True,
                "message": "Model is valid according to GO-CAM schema",
                "model": gocam_model.model_dump(exclude_none=True)
            }
        except ValidationError as e:
            errors = []
            for error in e.errors():
                errors.append({
                    "loc": " -> ".join([str(loc) for loc in error["loc"]]),
                    "msg": error["msg"],
                    "type": error["type"]
                })
            
            return {
                "valid": False,
                "message": "Model validation failed",
                "errors": errors
            }
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error validating GO-CAM model: {str(e)}")
