"""
CLI commands for the PaperQA agent.
"""
import os
import asyncio
import click

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
@click.option(
    "--force", "-f", is_flag=True, 
    help="Force reindex all papers",
)
def index(directory, force):
    """Index papers for search and querying."""
    config = get_config()
    if directory:
        config.paper_directory = directory
    
    paper_dir = config.paper_directory
    settings = config.get_paperqa_settings()
    
    if not os.path.exists(paper_dir):
        click.echo(f"Creating paper directory: {paper_dir}")
        os.makedirs(paper_dir, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(paper_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        click.echo(f"No PDF files found in {paper_dir}")
        return
    
    click.echo(f"Found {len(pdf_files)} PDF files in {paper_dir}")
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