"""
Tools for the PaperQA agent.
"""
import asyncio
import os
from typing import List, Dict, Any, Optional

from pydantic_ai import RunContext, ModelRetry

from paperqa import Docs, Settings, agent_query
from paperqa.agents.search import get_directory_index

from aurelian.utils.async_utils import run_sync
from .paperqa_config import PaperQADependencies


async def search_papers(
    ctx: RunContext[PaperQADependencies],
    query: str,
    max_papers: Optional[int] = None,
) -> Any:
    """
    Search for papers relevant to the query using PaperQA.

    Args:
        ctx: The run context
        query: The search query
        max_papers: Maximum number of papers to return (overrides config)

    Returns:
        The full PaperQA response object with search results
    """
    try:
        settings = ctx.deps.get_paperqa_settings()

        if max_papers is not None:
            settings.agent.search_count = max_papers

        await get_directory_index(settings=settings, build=False)

        response = await agent_query(
            query=f"Find scientific papers about: {query}",
            settings=settings
        )

        return response
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching papers: {str(e)}")


async def query_papers(
    ctx: RunContext[PaperQADependencies],
    query: str,
) -> Any:
    """
    Query the papers to answer a specific question using PaperQA.

    Args:
        ctx: The run context
        query: The question to answer based on the papers

    Returns:
        The full PQASession object with the answer and context
    """
    try:
        settings = ctx.deps.get_paperqa_settings()

        await get_directory_index(settings=settings, build=False)

        response = await agent_query(
            query=query,
            settings=settings
        )

        return response
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error querying papers: {str(e)}")


async def add_paper(
    ctx: RunContext[PaperQADependencies],
    path: str,
    citation: Optional[str] = None,
) -> Any:
    """
    Add a specific paper to the collection.

    Args:
        ctx: The run context
        path: Path to the paper file or URL
        citation: Optional citation for the paper

    Returns:
        Information about the added paper
    """
    try:
        settings = ctx.deps.get_paperqa_settings()
        docs = Docs()
        if path.startswith(("http://", "https://")):
            docname = await docs.aadd_url(
                url=path,
                citation=citation,
                settings=settings,
            )
        else:
            if not os.path.isabs(path):
                full_path = os.path.join(ctx.deps.paper_directory, path)
                if os.path.exists(full_path):
                    path = full_path
                else:
                    full_path = os.path.join(ctx.deps.workdir.location, path)
                    if os.path.exists(full_path):
                        path = full_path

            docname = await docs.aadd(
                path=path,
                citation=citation,
                settings=settings,
            )

        # Return info about the doc that was added
        if docname:
            doc = next((d for d in docs.docs.values() if d.docname == docname), None)
            return {
                "success": True,
                "docname": docname,
                "doc": doc
            }
        else:
            return {
                "success": False,
                "message": "Paper was already in the collection."
            }
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error adding paper: {str(e)}")


async def add_papers(
        ctx: RunContext[PaperQADependencies],
        directory: str,
) -> Any:
    """
    Add multiple papers from a directory to the collection.

    Args:
        ctx: The run context
        directory: Path to the directory containing papers

    Returns:
        Information about the added papers
    """
    try:
        settings = ctx.deps.get_paperqa_settings()

        if not os.path.isdir(directory):
            full_path = os.path.join(ctx.deps.paper_directory, directory)
            if os.path.isdir(full_path):
                directory = full_path
            else:
                full_path = os.path.join(ctx.deps.workdir.location, directory)
                if os.path.isdir(full_path):
                    directory = full_path
                else:
                    return {
                        "success": False,
                        "message": f"Directory not found: {directory}"
                    }

        pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]

        if not pdf_files:
            return {
                "success": False,
                "message": f"No PDF files found in directory: {directory}"
            }

        docs = Docs()
        added_papers = []

        for pdf_file in pdf_files:
            file_path = os.path.join(directory, pdf_file)
            try:
                docname = await docs.aadd(
                    path=file_path,
                    settings=settings,
                )
                if docname:
                    doc = next((d for d in docs.docs.values() if d.docname == docname), None)
                    added_papers.append({
                        "file": pdf_file,
                        "docname": docname,
                        "doc": doc
                    })
            except Exception as e:
                print(f"Error adding {file_path}: {e}")

        # Update the index with the added papers
        # This will trigger a reindex of the paper directory
        await get_directory_index(settings=settings, build=True)

        return {
            "success": True,
            "directory": directory,
            "papers_found": len(pdf_files),
            "papers_added": len(added_papers),
            "added_papers": added_papers
        }
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error adding papers: {str(e)}")


async def list_papers(
    ctx: RunContext[PaperQADependencies],
) -> Any:
    """
    List all papers in the current paper directory.

    Args:
        ctx: The run context

    Returns:
        Information about all papers in the paper directory
    """
    try:
        settings = ctx.deps.get_paperqa_settings()

        try:
            index = await get_directory_index(settings=settings, build=False)

            index_files = await index.index_files

            return {
                "success": True,
                "paper_directory": settings.agent.index.paper_directory,
                "paper_count": len(index_files),
                "indexed_files": list(index_files.keys()),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "No papers have been indexed yet. Use the 'aurelian paperqa index' command to index papers."
            }
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error listing papers: {str(e)}")