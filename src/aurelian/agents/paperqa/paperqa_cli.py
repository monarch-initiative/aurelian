"""
CLI commands for the PaperQA agent.
"""
import os
import asyncio
import logging
import sys
from pathlib import Path
import click
from paperqa import agent_query

from aurelian.agents.paperqa.paperqa_config import get_config
from paperqa.agents.search import get_directory_index
from paperqa.settings import IndexSettings

logger = logging.getLogger(__name__)

def setup_logging():
    """Set up logging for the PaperQA CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def check_api_key():
    """Check if the OpenAI API key is set.

    Returns:
        bool: True if key is set, False otherwise
    """
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable must be set.")
        click.echo("Error: OPENAI_API_KEY environment variable must be set.")
        return False
    return True


def setup_and_configure_paper_directory(directory):
    """
    Setup and configure a paper directory with proper paths.

    Args:
        directory: Input directory path (can be relative)

    Returns:
        tuple: (resolved_path, settings, config) tuple with properly configured settings
    """
    directory = str(Path(directory).resolve())

    config = get_config()
    config.paper_directory = directory

    os.environ["PQA_HOME"] = directory

    if not os.path.exists(directory):
        logger.info(f"Creating paper directory: {directory}")
        os.makedirs(directory, exist_ok=True)

    settings = config.set_paperqa_settings()
    settings.agent.index = IndexSettings(
        name=config.index_name,
        paper_directory=directory,
        recurse_subdirectories=False
    )

    return directory, settings, config


def get_document_files(directory):
    """
    Get all indexable document files in the given directory.

    Args:
        directory: Directory to search for document files

    Returns:
        dict: Dictionary with file lists by type and a combined list
    """
    document_extensions = ['.pdf', '.txt', '.html', '.md']
    all_files = [f for f in os.listdir(directory)
                if any(f.lower().endswith(ext) for ext in document_extensions)]

    return {
        'all': all_files,
        'pdf': [f for f in all_files if f.lower().endswith('.pdf')],
        'txt': [f for f in all_files if f.lower().endswith('.txt')],
        'html': [f for f in all_files if f.lower().endswith('.html')],
        'md': [f for f in all_files if f.lower().endswith('.md')],
    }


@click.group(name="paperqa")
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (-v for INFO, -vv for DEBUG)")
@click.option("-q", "--quiet", is_flag=True, help="Suppress non-error output")
def paperqa_cli(verbose, quiet):
    """PaperQA management commands for indexing and querying documents.
    
    PaperQA supports PDF, TXT, HTML, and Markdown files in all operations.
    
    Examples:
        # Index documents in a directory
        aurelian paperqa index -d /path/to/papers
        
        # Ask a question about indexed papers
        aurelian paperqa ask "What is the role of tau protein in Alzheimer's?" -d /path/to/papers
        
        # List indexed papers
        aurelian paperqa list -d /path/to/papers
        
        # Run with increased verbosity
        aurelian paperqa --verbose index -d /path/to/papers
        
        # Add documents through the agent
        # (Using these commands in chat modes like Gradio or MCP)
        "Add the paper from /path/to/paper.pdf"
        "Add all papers from the directory /path/to/papers/"
    """
    setup_logging()

    if verbose >= 2:
        logging.getLogger("aurelian.agents.paperqa").setLevel(logging.DEBUG)
    elif verbose == 1:
        logging.getLogger("aurelian.agents.paperqa").setLevel(logging.INFO)
    else:
        logging.getLogger("aurelian.agents.paperqa").setLevel(logging.WARNING)

    if quiet:
        logging.getLogger("aurelian.agents.paperqa").setLevel(logging.ERROR)


@paperqa_cli.command()
@click.option(
    "--directory", "-d", 
    required=True,
    help="Paper directory containing PDF, TXT, HTML, and MD files to index",
)
def index(directory):
    """Index documents for search and querying.
    
    This command scans the specified directory for documents (PDF, TXT, HTML, MD)
    and creates a searchable index for them. The index is stored in the .pqa
    subdirectory of the specified directory.
    
    Example:
        aurelian paperqa index -d ~/research/papers
    """
    if not check_api_key():
        return

    paper_dir, settings, _ = setup_and_configure_paper_directory(directory)

    docs = get_document_files(paper_dir)

    if not docs['all']:
        logger.warning(f"No indexable documents found in {paper_dir}")
        click.echo(f"No indexable documents found in {paper_dir}")
        return

    # detailed breakdown
    logger.info(f"Found {len(docs['all'])} documents in {paper_dir}:")
    if docs['pdf']: logger.info(f"  - {len(docs['pdf'])} PDF files")
    if docs['txt']: logger.info(f"  - {len(docs['txt'])} text files")
    if docs['html']: logger.info(f"  - {len(docs['html'])} HTML files")
    if docs['md']: logger.info(f"  - {len(docs['md'])} Markdown files")
    logger.info(f"Index will be stored in: {paper_dir}/.pqa")
    logger.info("Indexing papers... (this may take a while)")

    async def run_index():
        try:
            index = await get_directory_index(
                settings=settings,
                build=True,
            )
            index_files = await index.index_files
            logger.info(f"Success! Indexed {len(index_files)} document chunks from your PDF files.")
        except Exception as e:
            logger.error(f"Error indexing papers: {str(e)}")

    try:
        asyncio.run(run_index())
    except Exception as e:
        logger.error(f"Error: {str(e)}")


@paperqa_cli.command()
@click.argument("query", required=True)
@click.option(
"--directory", "-d",
required=True,
help="Paper directory containing indexed documents",
)
def ask(query, directory):
    """Ask a question about the indexed documents.
    
    This command searches the indexed documents for information relevant to the
    provided query and generates an AI-powered answer with references. Make sure
    to run the 'index' command first to create an index.
    
    Example:
        aurelian paperqa ask "What are the key findings on tau proteins?" -d ~/research/papers
    """
    if not check_api_key():
        return

    paper_dir, settings, _ = setup_and_configure_paper_directory(directory)

    async def run_query():
        try:
            docs = get_document_files(paper_dir)

            if not docs['all']:
                logger.warning(f"No indexable documents found in {paper_dir}")
                logger.info(f"Add documents (PDF, TXT, HTML, MD) to the directory and then run 'aurelian paperqa index -d {paper_dir}'")
                return

            try:
                index = await get_directory_index(settings=settings, build=False)
                index_files = await index.index_files

                if not index_files:
                    logger.warning(f"No indexed papers found. PDF files exist but haven't been indexed.")
                    logger.info(f"Run 'aurelian paperqa index -d {paper_dir}' to index the papers.")
                    return
            except Exception as e:
                if "was empty, please rebuild it" in str(e):
                    logger.warning(f"Index is empty. Run 'aurelian paperqa index -d {paper_dir}' to index papers.")
                    return
                raise

            logger.info(f"Querying {len(index_files)} papers about: {query}")
            logger.info("This may take a moment...")

            response = await agent_query(
                query=query,
                settings=settings
            )

            click.echo(f"Answer: {response.session.answer}" +
                       f"\n\nReferences: {response.session.references}")

        except Exception as e:
            logger.error(f"Error querying papers: {str(e)}")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_query())
    except Exception as e:
        logger.error(f"Error: {str(e)}")


@paperqa_cli.command()
@click.option(
    "--directory", "-d", 
    required=True,
    help="Paper directory containing documents",
)
def list(directory):
    """List documents in the directory and their indexing status.
    
    This command displays all documents (PDF, TXT, HTML, MD) in the specified
    directory and shows which ones have been indexed. Use this to verify that
    your documents are properly recognized and indexed.
    
    Example:
        aurelian paperqa list -d ~/research/papers
    """
    if not check_api_key():
        return
    
    paper_dir, settings, _ = setup_and_configure_paper_directory(directory)

    docs = get_document_files(paper_dir)

    logger.info(f"Documents in directory {paper_dir}:")
    for doc in docs['all']:
        if doc.lower().endswith('.pdf'):
            logger.info(f"  - {doc} [PDF]")
        elif doc.lower().endswith('.txt'):
            logger.info(f"  - {doc} [TXT]")
        elif doc.lower().endswith('.html'):
            logger.info(f"  - {doc} [HTML]")
        elif doc.lower().endswith('.md'):
            logger.info(f"  - {doc} [MD]")
    
    async def list_indexed():
        try:
            index = await get_directory_index(settings=settings, build=False)
            index_files = await index.index_files
            if index_files:
                logger.info(f"Indexed papers ({len(index_files)}):")
                for file in index_files:
                    logger.info(f"  - {file}")
            else:
                logger.warning(f"No indexed papers found. Run 'aurelian paperqa index -d {paper_dir}' to index papers.")
        except Exception as e:
            logger.error(f"Error accessing index: {str(e)}")
            logger.info(f"Run 'aurelian paperqa index -d {paper_dir}' to create or rebuild the index.")
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(list_indexed())
    except Exception as e:
        logger.error(f"Error: {str(e)}")