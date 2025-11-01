#!/usr/bin/env python3
"""
Test D4D agent using Claude Code's built-in Claude access instead of API tokens.
This approach uses Claude Code's native capabilities rather than external API calls.
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import aurelian modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aurelian.agents.d4d.d4d_config import D4DConfig
from aurelian.agents.d4d.d4d_tools import get_full_schema, process_website_or_pdf


async def extract_with_builtin_claude():
    """Use Claude Code's built-in capabilities to extract D4D metadata."""
    
    print("D4D Agent using Claude Code Built-in Access")
    print("=" * 50)
    
    # Configure the agent
    config = D4DConfig()
    
    # Sample dataset URL
    sample_url = "https://archive.ics.uci.edu/ml/datasets/wine"
    
    print(f"Processing dataset: {sample_url}")
    print("Loading schema and extracting content...")
    
    try:
        # Load the D4D schema
        schema = await get_full_schema(None, config.schema_url)
        print(f"✅ Schema loaded ({len(schema.split())} words)")
        
        # Extract content from the URL
        content = await process_website_or_pdf(config, sample_url)
        print(f"✅ Content extracted ({len(content.split())} words)")
        
        # Create the prompt for Claude Code to process
        prompt = f"""
You are an expert data scientist specializing in extracting metadata from datasets following the "Datasheets for Datasets" schema.

Below is the complete D4D schema:
---
{schema[:3000]}...
---

Dataset content to process:
---
{content[:2000]}...
---

Please extract all relevant metadata from the dataset content and generate a complete YAML document that strictly follows the D4D schema above. Focus on:
- Dataset identity (id, name, title, description)
- Creators and contributors
- Purpose and intended uses
- Data composition and structure
- Collection methodology
- Preprocessing steps
- Distribution information
- Licensing and terms of use
- Maintenance information

Generate only valid YAML output without any additional commentary.
"""
        
        print("\n" + "="*50)
        print("D4D METADATA EXTRACTION REQUEST:")
        print("="*50)
        print(f"Schema loaded: {len(schema)} characters")
        print(f"Content extracted: {len(content)} characters") 
        print(f"Ready to process with built-in Claude...")
        
        # The actual Claude processing would happen here in Claude Code environment
        print("\nTo complete this extraction, Claude Code would now:")
        print("1. Process the full schema and dataset content")
        print("2. Extract all relevant D4D metadata")
        print("3. Generate valid YAML following the schema")
        print("4. Output the complete D4D datasheet")
        
        return prompt
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    prompt = asyncio.run(extract_with_builtin_claude())
    
    print("\n" + "="*50)
    print("PROMPT FOR CLAUDE CODE:")
    print("="*50)
    print(prompt[:1000] + "...")