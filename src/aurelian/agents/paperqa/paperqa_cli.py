"""
CLI commands for the PaperQA agent.
"""
import os
import asyncio
import click

from aurelian.agents.paperqa.paperqa_config import get_config, PaperQADependencies
from paperqa.agents.search import get_directory_index
from paperqa import agent_query


@click.group(name="paperqa")
def paperqa_cli():
    """PaperQA management commands."""
    pass


@paperqa_cli.command()
@click.option(
    "--directory", "-d",
    help="Paper directory (override config)",
    required=True,
)
def index(directory):
    """Index papers for search and querying."""

    config=PaperQADependencies(paper_directory=directory)
    settings = config.set_paperqa_settings(
        paper_directory=directory
    )

    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]

    if not pdf_files:
        click.echo(f"No PDF files found in {directory}")
        return

    click.echo(f"Found {len(pdf_files)} PDF files in {directory}")
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

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_index())
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@paperqa_cli.command()
@click.option(
    "--directory", "-d",
    help="Paper directory (override config)",
)
def list(directory):
    """List indexed papers."""
    config=PaperQADependencies(paper_directory=directory)
    settings = config.set_paperqa_settings(
        paper_directory=directory
    )

    if not os.path.exists(directory):
        click.echo(f"Paper directory does not exist: {directory}")
        return

    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]

    click.echo(f"Files in paper directory {directory}:")
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


@paperqa_cli.command()
@click.argument("query", required=True)
@click.option(
    "--directory", "-d",
    help="Paper directory (override config)",
)
def ask(query, directory):
    """Ask a question about the indexed papers."""

    config = PaperQADependencies(paper_directory=directory)
    settings = config.set_paperqa_settings(
        paper_directory=directory
    )

    if not os.path.exists(directory):
        click.echo(f"Paper directory does not exist: {directory}")
        return

    async def run_query():
        try:
            # First check if papers are indexed
            index = await get_directory_index(settings=settings, build=False)
            index_files = await index.index_files

            if not index_files:
                raise RuntimeError("No indexed papers found. Run 'aurelian paperqa index' to index papers.")

            click.echo(f"Querying {len(index_files)} papers about: {query}")
            click.echo("This may take a moment...\n")

            response = await agent_query(
                query=query,
                settings=settings
            )

            click.echo(f"Answer: {response.answer}")

            if hasattr(response, 'context') and response.context:
                click.echo("\nSources:")
                for i, ctx in enumerate(response.context):
                    click.echo(f"[{i+1}] {ctx.docname}: {ctx.citation or 'No citation'}")

        except Exception as e:
            click.echo(f"Error querying papers: {str(e)}")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_query())
    except Exception as e:
        click.echo(f"Error: {str(e)}")
