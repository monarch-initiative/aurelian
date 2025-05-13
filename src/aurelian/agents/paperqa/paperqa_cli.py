"""
CLI commands for the PaperQA agent.
"""
import os
import asyncio
import click
from paperqa import agent_query

from aurelian.agents.paperqa.paperqa_config import get_config
from paperqa.agents.search import get_directory_index


@click.group(name="paperqa")
def paperqa_cli():
    """PaperQA management commands."""
    pass


@paperqa_cli.command()
@click.option(
    "--directory", "-d", 
    help="Paper directory (override config)",
)
@click.option("--index-location", "-i", help="Paper index location")
def index(directory, index_location):
    """Index papers for search and querying."""
    config = get_config()
    if directory:
        config.paper_directory = directory

    paper_dir = config.paper_directory

    # Make index location the same as paper directory if not specified
    if not index_location:
        index_location = paper_dir

    # Set PQA_HOME environment variable to control where PaperQA stores index files
    os.environ["PQA_HOME"] = index_location

    # Create PaperQA settings with index_absolute_directory=True to ensure
    # indexes are stored with the papers
    settings = config.get_paperqa_settings()

    from paperqa.settings import IndexSettings
    settings.agent.index = IndexSettings(
        name=config.index_name,
        paper_directory=paper_dir,
        index_directory=index_location,
        # use_absolute_paper_directory=True
    )

    if not os.path.exists(paper_dir):
        click.echo(f"Creating paper directory: {paper_dir}")
        os.makedirs(paper_dir, exist_ok=True)

    pdf_files = [f for f in os.listdir(paper_dir) if f.lower().endswith('.pdf')]

    if not pdf_files:
        click.echo(f"No PDF files found in {paper_dir}")
        return

    click.echo(f"Found {len(pdf_files)} PDF files in {paper_dir}")
    click.echo(f"Index will be stored in: {index_location}")
    click.echo("Indexing papers... (this may take a while)")

    async def run_index():
        try:
            index = await get_directory_index(
                settings=settings,
                build=True,
            )
            index_files = await index.index_files
            click.echo(f"Success! {len(index_files)} papers indexed.")
        except Exception as e:
            click.echo(f"Error indexing papers: {str(e)}")

    try:
        asyncio.run(run_index())
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@paperqa_cli.command()
@click.argument("query", required=True)
@click.option(
"--directory", "-d",
help="Paper directory (override config)",
)
@click.option("--index-location", "-i", help="Paper index location")
def ask(query, directory, index_location):
    """Ask a question about the indexed papers."""
    config = get_config()
    if directory:
        config.paper_directory = directory

    paper_dir = config.paper_directory

    # Make index location the same as paper directory if not specified
    # to index on same spot where pdfs
    if not index_location:
        index_location = paper_dir

    # Set PQA_HOME environment variable to control where PaperQA stores index files
    os.environ["PQA_HOME"] = index_location

    # Create PaperQA settings
    settings = config.get_paperqa_settings()

    # Update settings with custom index location
    from paperqa.settings import IndexSettings
    settings.agent.index = IndexSettings(
        name=config.index_name,
        paper_directory=paper_dir,
        index_directory=index_location,
    )

    if not os.path.exists(paper_dir):
        click.echo(f"Paper directory does not exist: {paper_dir}")
        return

    async def run_query():
        try:
            # First check if papers are indexed
            index = await get_directory_index(settings=settings, build=False)
            index_files = await index.index_files

            if not index_files:
                raise RuntimeError("No indexed papers found. Run "
                                   "'aurelian paperqa index' to index papers.")

            click.echo(f"Querying {len(index_files)} papers about: {query}")
            click.echo("This may take a moment...\n")

            response = await agent_query(
                query=query,
                settings=settings
            )

            answer = response.session.context


            click.echo(f"Answer: {response.session.answer}" +
                       f"\n\nReferences: {response.session.references}")

        except Exception as e:
            click.echo(f"Error querying papers: {str(e)}")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_query())
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@paperqa_cli.command()
@click.option(
    "--directory", "-d", 
    help="Paper directory (override config)",
)
def list(directory):
    """List indexed papers."""
    config = get_config()
    if directory:
        config.paper_directory = directory
    
    paper_dir = config.paper_directory
    settings = config.get_paperqa_settings()
    
    if not os.path.exists(paper_dir):
        click.echo(f"Paper directory does not exist: {paper_dir}")
        return
    
    pdf_files = [f for f in os.listdir(paper_dir) if f.lower().endswith('.pdf')]
    
    click.echo(f"Files in paper directory {paper_dir}:")
    for pdf in pdf_files:
        click.echo(f"  - {pdf}")
    
    async def list_indexed():
        try:
            index = await get_directory_index(settings=settings, build=False)
            index_files = await index.index_files
            click.echo(f"\nIndexed papers ({len(index_files)}):")
            for file in index_files:
                click.echo(f"  - {file}")
        except Exception as e:
            click.echo(f"\nNo indexed papers found. Run 'aurelian paperqa index' to index papers.")
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(list_indexed())
    except Exception as e:
        click.echo(f"Error: {str(e)}")