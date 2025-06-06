"""
Command Line Interface for Schema Generator Agent.
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from .schema_agent import run_with_validation
from .schema_config import get_schema_config


@click.group()
def schema_cli():
    """Schema Generator CLI - Create and validate LinkML schemas for extraction."""
    pass


@schema_cli.command()
@click.argument('description', type=str)
@click.option('--output', '-o', type=click.Path(), help='Output file for generated schema')
@click.option('--model', default='openai:gpt-4o', help='Model to use for generation')
@click.option('--validate-only', is_flag=True, help='Only validate, do not save')
def generate(description: str, output: Optional[str], model: str, validate_only: bool):
    """
    Generate a LinkML schema from a description.
    
    DESCRIPTION: What you want to extract (e.g., "genes and diseases from biomedical text")
    
    Examples:
    
        schema generate "genes and diseases from biomedical text"
        
        schema generate "chemical reactions with yields and conditions" -o chemistry.yaml
        
        schema generate "houses, streets, and prices from real estate listings"
    """
    async def _generate():
        deps = get_schema_config()
        
        click.echo(f"🔧 Generating schema for: {description}")
        click.echo(f"Model: {model}")
        
        try:
            # Generate and validate schema
            schema_yaml = await run_with_validation(description, deps)
            
            if "validation failed" in schema_yaml.lower() or "error" in schema_yaml.lower():
                click.echo(f"{schema_yaml}")
                sys.exit(1)
            
            click.echo("Schema generated and validated successfully!")
            
            if validate_only:
                click.echo("\n📋 Generated Schema:")
                click.echo(schema_yaml)
            elif output:
                # Save to file
                output_path = Path(output)
                output_path.write_text(schema_yaml)
                click.echo(f"💾 Schema saved to: {output_path}")
            else:
                # Print to stdout
                click.echo("\n📋 Generated Schema:")
                click.echo(schema_yaml)
                
        except Exception as e:
            click.echo(f"Error: {e}")
            sys.exit(1)
    
    asyncio.run(_generate())


@schema_cli.command()
@click.argument('schema_file', type=click.Path(exists=True))
def validate(schema_file: str):
    """
    Validate an existing LinkML schema file.
    
    SCHEMA_FILE: Path to the LinkML schema YAML file to validate
    
    Examples:
    
        schema validate my_schema.yaml
        
        schema validate /path/to/gene_extraction.yaml
    """
    async def _validate():
        try:
            schema_path = Path(schema_file)
            schema_content = schema_path.read_text()
            
            click.echo(f"🔍 Validating schema: {schema_path}")
            
            # Use LinkML validation directly
            from aurelian.agents.linkml.linkml_tools import validate_then_save_schema
            from aurelian.agents.linkml.linkml_config import get_config as get_linkml_config
            
            class MockContext:
                def __init__(self, deps):
                    self.deps = deps
            
            linkml_deps = get_linkml_config()
            ctx = MockContext(linkml_deps)
            
            result = await validate_then_save_schema(ctx, schema_content, None)
            
            if result.valid:
                click.echo("Schema is valid!")
                if result.info_messages:
                    for msg in result.info_messages:
                        click.echo(f"ℹ️  {msg}")
            else:
                click.echo("Schema validation failed")
                sys.exit(1)
                
        except Exception as e:
            click.echo(f"Validation error: {e}")
            sys.exit(1)
    
    asyncio.run(_validate())

if __name__ == "__main__":
    schema_cli()