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
        A simplified response with paper details and metadata
    """
    try:
        settings = ctx.deps.set_paperqa_settings()

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
        settings = ctx.deps.set_paperqa_settings()

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


async def build_index(
    ctx: RunContext[PaperQADependencies],
) -> Any:
    """
    Rebuild the search index for papers.

    Args:
        ctx: The run context

    Returns:
        Information about the indexing process
    """
    try:
        settings = ctx.deps.set_paperqa_settings()
        paper_directory = settings.agent.index.paper_directory

        os.makedirs(paper_directory, exist_ok=True)

        pdf_files = []
        if os.path.exists(paper_directory):
            for file in os.listdir(paper_directory):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(file)

        if not pdf_files:
            return {
                "success": True,
                "paper_directory": paper_directory,
                "indexed_papers_count": 0,
                "indexed_papers": [],
                "message": f"No PDF files found in {paper_directory}. Add PDFs to this directory before indexing."
            }

        try:
            # Force a rebuild of the index
            print(f"Building index for {len(pdf_files)} PDF files in {paper_directory}...")
            index = await get_directory_index(settings=settings, build=True)
            index_files = await index.index_files

            if not index_files:
                # The index is still empty despite finding PDFs - this could be a parsing issue
                return {
                    "success": True,
                    "paper_directory": paper_directory,
                    "pdf_files_found": pdf_files,
                    "pdf_files_count": len(pdf_files),
                    "indexed_papers_count": 0,
                    "indexed_papers": [],
                    "message": f"Found {len(pdf_files)} PDF files but none were successfully indexed. This could be due to parsing issues with the PDFs."
                }

            return {
                "success": True,
                "paper_directory": paper_directory,
                "pdf_files_count": len(pdf_files),
                "indexed_papers_count": len(index_files),
                "indexed_papers": list(index_files.keys()),
                "message": f"Successfully indexed {len(index_files)} papers out of {len(pdf_files)} PDF files."
            }
        except Exception as e:
            return {
                "success": False,
                "paper_directory": paper_directory,
                "pdf_files_found": pdf_files,
                "pdf_files_count": len(pdf_files),
                "error": str(e),
                "message": f"Error indexing papers: {str(e)}"
            }
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error building index: {str(e)}")


async def add_paper(
    ctx: RunContext[PaperQADependencies],
    path: str,
    citation: Optional[str] = None,
    auto_index: bool = True,
) -> Any:
    """
    Add a specific paper to the collection.

    Args:
        ctx: The run context
        path: Path to the paper file or URL
        citation: Optional citation for the paper
        auto_index: Whether to automatically rebuild the index after adding the paper

    Returns:
        Information about the added paper
    """
    try:
        settings = ctx.deps.set_paperqa_settings()

        # Ensure the paper directory exists
        paper_directory = settings.agent.index.paper_directory
        os.makedirs(paper_directory, exist_ok=True)

        # For URLs, we need to:
        # 1. Download the PDF
        # 2. Save it to the paper directory
        # 3. Process it with Docs

        if path.startswith(("http://", "https://")):
            import requests
            from urllib.parse import urlparse

            url_parts = urlparse(path)
            file_name = os.path.basename(url_parts.path)
            if not file_name or not file_name.lower().endswith('.pdf'):
                file_name = "paper.pdf"

            target_path = os.path.join(paper_directory, file_name)

            try:
                response = requests.get(path, stream=True)
                response.raise_for_status()

                with open(target_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Downloaded {path} to {target_path}")

                docs = Docs()
                docname = await docs.aadd(
                    path=target_path,
                    citation=citation,
                    settings=settings,
                )
            except Exception as e:
                # If download fails, fall back to docs.aadd_url
                print(f"Download failed: {str(e)}, falling back to docs.aadd_url")
                docs = Docs()
                docname = await docs.aadd_url(
                    url=path,
                    citation=citation,
                    settings=settings,
                )

                # If we successfully added it with aadd_url, try to find where it saved the file
                if docname and hasattr(docs, 'docs') and docname in docs.docs:
                    doc = docs.docs[docname]
                    if hasattr(doc, 'filepath') and os.path.exists(doc.filepath):
                        import shutil
                        target_path = os.path.join(paper_directory, f"{docname}.pdf")
                        if not os.path.exists(target_path):
                            shutil.copy2(doc.filepath, target_path)
                            print(f"Copied from {doc.filepath} to {target_path}")
        else:
            # For file paths, copy to paper directory if needed
            if not os.path.isabs(path):
                full_path = os.path.join(ctx.deps.paper_directory, path)
                if os.path.exists(full_path):
                    path = full_path
                else:
                    full_path = os.path.join(ctx.deps.workdir.location, path)
                    if os.path.exists(full_path):
                        path = full_path

            # If the path is outside the paper directory, copy it there
            if os.path.exists(path) and paper_directory not in path:
                import shutil
                target_path = os.path.join(paper_directory, os.path.basename(path))
                if not os.path.exists(target_path):
                    shutil.copy2(path, target_path)

            docs = Docs()
            docname = await docs.aadd(
                path=path,
                citation=citation,
                settings=settings,
            )

        if docname:
            doc = next((d for d in docs.docs.values() if d.docname == docname), None)

            result = {
                "success": True,
                "docname": docname,
                "doc": doc,
            }

            if auto_index:
                try:
                    index_result = await build_index(ctx)
                    result["index_result"] = index_result
                    if index_result["success"]:
                        result["message"] = f"Paper added and indexed successfully. {index_result['indexed_papers_count']} papers now in the index."
                    else:
                        result["message"] = f"Paper added but indexing failed: {index_result['error']}"
                except Exception as e:
                    result["message"] = f"Paper added but indexing failed: {str(e)}"
            else:
                result["message"] = "Paper added successfully. Use 'aurelian paperqa index' to rebuild the index to make this paper searchable."

            return result
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
        settings = ctx.deps.set_paperqa_settings()

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
        settings = ctx.deps.set_paperqa_settings()
        paper_directory = settings.agent.index.paper_directory

        pdf_files = []
        if os.path.exists(paper_directory):
            for file in os.listdir(paper_directory):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(file)

        indexed_files = []
        try:
            index = await get_directory_index(settings=settings, build=False)
            index_files = await index.index_files
            indexed_files = list(index_files.keys())
        except Exception as e:
            # Index may not exist yet, which is fine
            pass

        return {
            "success": True,
            "paper_directory": paper_directory,
            "files_in_directory": pdf_files,
            "files_in_directory_count": len(pdf_files),
            "indexed_files": indexed_files,
            "indexed_files_count": len(indexed_files),
            "note": "To search papers, they must be both in the paper directory AND indexed. If there are files in the directory but not indexed, use the CLI command 'aurelian paperqa index' to index them."
        }
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error listing papers: {str(e)}")
