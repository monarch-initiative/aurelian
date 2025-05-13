"""
Tools for the PaperQA agent.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from pydantic_ai import RunContext, ModelRetry

from paperqa import Docs, agent_query
from paperqa.agents.search import get_directory_index

from .paperqa_config import PaperQADependencies


def create_response(success: bool, paper_directory: str, doc_files: dict,
                    indexed_files: Optional[dict] = None, **kwargs) -> dict:
    """Create a standardized response dictionary.
    
    Args:
        success: Whether the operation was successful
        paper_directory: Path to the paper directory
        doc_files: Dictionary with document files by type
        indexed_files: Optional dictionary of indexed files
        **kwargs: Additional key-value pairs to include in the response
        
    Returns:
        A standardized response dictionary
    """
    document_counts = {
        'total': len(doc_files['all']),
        'pdf': len(doc_files['pdf']),
        'txt': len(doc_files['txt']),
        'html': len(doc_files['html']),
        'md': len(doc_files['md']),
    }
    
    response = {
        "success": success,
        "paper_directory": paper_directory,
        "document_counts": document_counts,
    }
    
    if indexed_files is not None:
        response["indexed_chunks_count"] = len(indexed_files)
        response["indexed_papers"] = list(indexed_files.keys()) if hasattr(indexed_files, 'keys') else []
    
    response.update(kwargs)
    
    return response

logger = logging.getLogger(__name__)


def get_document_files(directory: str) -> Dict[str, List[str]]:
    """
    Get all indexable document files in the given directory.
    
    Args:
        directory: Directory to search for document files
        
    Returns:
        dict: Dictionary with file lists by type and a combined list
    """
    document_extensions = ['.pdf', '.txt', '.html', '.md']
    all_files = []
    
    dir_path = Path(directory)
    if dir_path.exists() and dir_path.is_dir():
        all_files = [f.name for f in dir_path.iterdir() 
                    if f.is_file() and any(f.name.lower().endswith(ext) for ext in document_extensions)]
    
    return {
        'all': all_files,
        'pdf': [f for f in all_files if f.lower().endswith('.pdf')],
        'txt': [f for f in all_files if f.lower().endswith('.txt')],
        'html': [f for f in all_files if f.lower().endswith('.html')],
        'md': [f for f in all_files if f.lower().endswith('.md')],
    }


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

        try:
            index = await get_directory_index(settings=settings, build=False)
            index_files = await index.index_files
            logger.info(f"Found existing index with {len(index_files)} files")
        except Exception as e:
            # If the error is about an empty index, try to build it
            if "was empty, please rebuild it" in str(e):
                logger.info("Index is empty, attempting to rebuild...")
                index = await get_directory_index(settings=settings, build=True)
                index_files = await index.index_files

                if not index_files:
                    return {
                        "message": "No papers are currently indexed. You can add papers using the add_paper function.",
                        "papers": []
                    }
            else:
                raise

        response = await agent_query(
            query=f"Find scientific papers about: {query}",
            settings=settings
        )

        return response
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e

        if "was empty, please rebuild it" in str(e):
            return {
                "message": "No papers are currently indexed. You can add papers using the add_paper function.",
                "papers": []
            }

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

        try:
            # First try to get the index without building
            index = await get_directory_index(settings=settings, build=False)
            index_files = await index.index_files

            # If we get here, the index exists and has files
            if not index_files:
                return {
                    "message": "No papers are currently indexed. You can add papers using the add_paper function.",
                    "papers": []
                }
        except Exception as e:
            if "was empty, please rebuild it" in str(e):
                return {
                    "message": "No papers are currently indexed. You can add papers using the add_paper function.",
                    "papers": []
                }
            else:
                raise

        response = await agent_query(
            query=query,
            settings=settings
        )

        return response
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e

        if "was empty, please rebuild it" in str(e):
            return {
                "message": "No papers are currently indexed. You can add papers using the add_paper function.",
                "papers": []
            }

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

        doc_files = get_document_files(paper_directory)

        if not doc_files['all']:
            return create_response(
                success=True,
                paper_directory=paper_directory,
                doc_files=doc_files,
                indexed_files={},
                message=f"No indexable documents found in {paper_directory}. Add documents (PDF, TXT, HTML, MD) to this directory before indexing."
            )

        try:
            logger.info(f"Building index for {len(doc_files['all'])} documents in {paper_directory}:")
            if doc_files['pdf']:
                logger.info(f"  - {len(doc_files['pdf'])} PDF files")
            if doc_files['txt']:
                logger.info(f"  - {len(doc_files['txt'])} text files")
            if doc_files['html']:
                logger.info(f"  - {len(doc_files['html'])} HTML files")
            if doc_files['md']:
                logger.info(f"  - {len(doc_files['md'])} Markdown files")
            
            index = await get_directory_index(settings=settings, build=True)
            index_files = await index.index_files

            if not index_files:
                return create_response(
                    success=True,
                    paper_directory=paper_directory,
                    doc_files=doc_files,
                    indexed_files={},
                    documents_found=doc_files,
                    message=f"Found {len(doc_files['all'])} documents but none were successfully indexed. This could be due to parsing issues with the documents."
                )

            return create_response(
                success=True,
                paper_directory=paper_directory,
                doc_files=doc_files,
                indexed_files=index_files,
                message=f"Successfully indexed {len(index_files)} document chunks from {len(doc_files['all'])} files."
            )
        except Exception as e:
            return create_response(
                success=False,
                paper_directory=paper_directory,
                doc_files=doc_files,
                message=f"Error indexing documents: {str(e)}",
                error=str(e)
            )
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

                logger.info(f"Downloaded {path} to {target_path}")

                docs = Docs()
                docname = await docs.aadd(
                    path=target_path,
                    citation=citation,
                    settings=settings,
                )
            except Exception as e:
                # If download fails, fall back to docs.aadd_url
                logger.warning(f"Download failed: {str(e)}, falling back to docs.aadd_url")
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
                            logger.info(f"Copied from {doc.filepath} to {target_path}")
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
        citation: Optional[str] = None,
        auto_index: bool = True,
) -> Any:
    """
    Add multiple papers from a directory to the collection.

    Args:
        ctx: The run context
        directory: Path to the directory containing papers
        citation: Optional citation format to use for all papers (paper filename will be appended)
        auto_index: Whether to automatically rebuild the index after adding the papers

    Returns:
        Information about the added papers
    """
    try:
        settings = ctx.deps.set_paperqa_settings()
        paper_directory = settings.agent.index.paper_directory
        os.makedirs(paper_directory, exist_ok=True)

        if not Path(directory).is_dir():
            return create_response(
                success=False,
                paper_directory=paper_directory,
                doc_files={"all": [], "pdf": [], "txt": [], "html": [], "md": []}
            )

        doc_files = get_document_files(directory)

        if not doc_files['all']:
            return create_response(
                success=False,
                paper_directory=paper_directory,
                doc_files=doc_files
            )

        logger.info(f"Found {len(doc_files['all'])} documents in {directory}:")
        if doc_files['pdf']:
            logger.info(f"  - {len(doc_files['pdf'])} PDF files")
        if doc_files['txt']:
            logger.info(f"  - {len(doc_files['txt'])} text files")
        if doc_files['html']:
            logger.info(f"  - {len(doc_files['html'])} HTML files")
        if doc_files['md']:
            logger.info(f"  - {len(doc_files['md'])} Markdown files")

        docs = Docs()
        added_papers = []

        for doc_file in doc_files['all']:
            file_path = os.path.join(directory, doc_file)
            try:
                logger.info(f"Adding document: {file_path}")
                
                doc_citation = None
                if citation:
                    doc_citation = f"{citation} - {doc_file}"
                
                if Path(file_path).exists() and paper_directory not in file_path:
                    import shutil
                    target_path = os.path.join(paper_directory, os.path.basename(file_path))
                    if not Path(target_path).exists():
                        shutil.copy2(file_path, target_path)
                        logger.info(f"Copied {file_path} to {target_path}")
                
                docname = await docs.aadd(
                    path=file_path,
                    citation=doc_citation,
                    settings=settings,
                )
                if docname:
                    doc = next((d for d in docs.docs.values() if d.docname == docname), None)
                    added_papers.append({
                        "file": doc_file,
                        "docname": docname,
                        "citation": doc_citation,
                        "doc": doc
                    })
                    logger.info(f"Successfully added document: {doc_file}")
            except Exception as e:
                logger.error(f"Error adding {file_path}: {e}")

        index_result = None
        if auto_index and added_papers:
            try:
                index_result = await build_index(ctx)
                logger.info(f"Index rebuilt with {len(index_result.get('indexed_papers', []))} papers")
            except Exception as e:
                logger.error(f"Error rebuilding index: {e}")
                index_result = {"success": False, "error": str(e)}
        
        response = create_response(
            success=True,
            paper_directory=paper_directory,
            doc_files=doc_files,
            message=f"Successfully added {len(added_papers)} documents out of {len(doc_files['all'])}",
            documents_added=len(added_papers),
            added_documents=added_papers
        )
        
        if index_result:
            response["index_result"] = index_result
            
        return response
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

        doc_files = get_document_files(paper_directory)
        
        indexed_files = []
        try:
            index = await get_directory_index(settings=settings, build=False)
            index_files = await index.index_files
            indexed_files = list(index_files.keys())
            logger.info(f"Found {len(indexed_files)} indexed document chunks")
        except Exception:
            logger.info("No index found or index is empty")

        return create_response(
            success=True,
            paper_directory=paper_directory,
            doc_files=doc_files,
            indexed_files=indexed_files,
            message=f"Found {len(doc_files['all'])} documents and {len(indexed_files)} indexed chunks",
            files_in_directory=doc_files['all'],
            files_by_type={
                "pdf": doc_files['pdf'],
                "txt": doc_files['txt'],
                "html": doc_files['html'],
                "md": doc_files['md']
            },
            note="To search papers, they must be both in the paper directory AND indexed. If there are files in the directory but not indexed, use the CLI command 'aurelian paperqa index -d <directory>' to index them."
        )
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error listing papers: {str(e)}")
