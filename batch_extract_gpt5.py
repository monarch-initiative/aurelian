#!/usr/bin/env python3
"""
Batch extraction script for running D4D extractions on all datasets with GPT-5.
"""
import asyncio
import os
import sys
import json
import hashlib
from pathlib import Path
from urllib.parse import urlparse

# Add the src directory to the path so we can import aurelian modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pydantic_ai import Agent
from aurelian.agents.d4d.d4d_config import D4DConfig
from aurelian.agents.d4d.d4d_tools import get_full_schema, process_website_or_pdf


# Create a D4D agent using GPT-5
gpt5_d4d_agent = Agent(
    model="openai:gpt-5",
    deps_type=D4DConfig,
    system_prompt="""
You are an expert data scientist specializing in extracting metadata from datasets. 
You will be provided with a schema that describes the metadata structure for datasets, 
and one or more URLs pointing to webpages or PDFs that describe a dataset. 
Your task is to extract all relevant metadata from the provided content and output it in
YAML format, strictly following the provided schema. Generate only the YAML document. 
Do not respond with any additional commentary. Try to ensure that required fields are 
present, but only populate items that you are sure about. Ensure that output is valid 
YAML. 

Below is the complete datasheets for datasets schema:

{schema}

For each URL to a webpage or PDF describing a dataset, you will fetch the
content, extract all the relevant metadata, and output a YAML document that exactly 
conforms to the above schema. The output must be valid YAML with all required fields 
filled in, following the schema exactly.

If you get more than one URL, assume they are describing the same dataset. Process each 
URL to retrieve information about the dataset, concatenate the content from all URLs,

You should return a single YAML document describing the dataset.
""",
    defer_model_check=True,
)


@gpt5_d4d_agent.system_prompt
async def add_schema(ctx) -> str:
    """Add the full schema to the system prompt."""
    schema = await get_full_schema(ctx)
    return schema


@gpt5_d4d_agent.tool
async def extract_metadata(ctx, urls: list[str], verbose: bool = True) -> str:
    """Extract metadata from dataset description documents or webpages."""
    content = ""
    for url in urls:
        if verbose:
            print(f"Processing URL: {url}")
        content += await process_website_or_pdf(ctx, url)

    prompt = f"""
The following is the content of one or more documents describing a dataset:

{content}

Using the complete datasheets for datasets schema provided above, extract all the metadata 
from the document and generate a YAML document that exactly conforms to that schema. 
"""
    return prompt


def url_to_filename(url: str) -> str:
    """Convert URL to a safe filename."""
    # Create a hash of the URL for uniqueness
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    
    # Extract domain and path for readability
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '').replace('.', '_')
    path_parts = [p for p in parsed.path.split('/') if p and p != 'dataset.xhtml']
    
    if path_parts:
        filename = f"{domain}_{'-'.join(path_parts[:2])}_{url_hash}"
    else:
        filename = f"{domain}_{url_hash}"
    
    # Clean filename
    filename = ''.join(c for c in filename if c.isalnum() or c in '-_')
    return f"{filename}_gpt5.yaml"


async def extract_single_dataset(url: str, output_dir: Path, config: D4DConfig):
    """Extract metadata for a single dataset URL."""
    output_file = output_dir / url_to_filename(url)
    
    # Skip if already exists
    if output_file.exists():
        print(f"Skipping {url} - output already exists: {output_file.name}")
        return True
    
    print(f"\n{'='*60}")
    print(f"Extracting: {url}")
    print(f"Output: {output_file.name}")
    print('='*60)
    
    try:
        # Run the agent
        result = await gpt5_d4d_agent.run(
            f"Extract dataset metadata from: {url}",
            deps=config
        )
        
        # Save the result
        with open(output_file, 'w') as f:
            f.write(result.output)
        
        print(f"✅ Successfully extracted metadata for {url}")
        return True
        
    except Exception as e:
        print(f"❌ Error extracting {url}: {e}")
        # Save error info
        error_file = output_file.with_suffix('.error')
        with open(error_file, 'w') as f:
            f.write(f"URL: {url}\nError: {str(e)}\n")
        return False


async def main():
    """Main batch extraction function."""
    
    # Check if we have an API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Define URLs to extract
    urls = [
        "https://dataverse.lib.virginia.edu/dataset.xhtml?persistentId=doi:10.18130/V3/B35XWX",
        "https://dataverse.lib.virginia.edu/dataset.xhtml?persistentId=doi:10.18130/V3/F3TD5R&version=DRAFT",
        "https://github.com/chorus-ai#table-of-contents",
        "https://healthdatanexus.ai/content/b2ai-voice/1.0/",
        "https://physionet.org/content/b2ai-voice/1.1/",
        "https://fairhub.io/datasets/2",
        "https://doi.org/10.1101/2024.05.21.589311",
        "https://doi.org/10.5281/zenodo.10642459",
        "https://docs.aireadi.org/docs/2/about",
        # Skipping malformed URL: "https://aireadi.org/publicationshttps://doi.org/10.1038/s42255-024-01165-xhttps://doi.org/10.1136/bmjopen-2024-097449"
        # Skipping Google Docs URL as it requires authentication
    ]
    
    # Setup output directory
    output_dir = Path("../extracted_datasets_v3")
    output_dir.mkdir(exist_ok=True)
    
    # Configure the agent
    config = D4DConfig()
    
    print(f"Starting batch extraction for {len(urls)} datasets...")
    print(f"Output directory: {output_dir.absolute()}")
    
    # Track results
    successful = 0
    failed = 0
    
    # Process each URL
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        try:
            success = await extract_single_dataset(url, output_dir, config)
            if success:
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Unexpected error processing {url}: {e}")
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("BATCH EXTRACTION COMPLETE")
    print('='*60)
    print(f"Total URLs processed: {len(urls)}")
    print(f"Successful extractions: {successful}")
    print(f"Failed extractions: {failed}")
    print(f"Output directory: {output_dir.absolute()}")
    
    # List generated files
    yaml_files = list(output_dir.glob("*_gpt5.yaml"))
    error_files = list(output_dir.glob("*.error"))
    
    print(f"\nGenerated files ({len(yaml_files)} YAML, {len(error_files)} errors):")
    for file in sorted(yaml_files):
        print(f"  ✅ {file.name}")
    for file in sorted(error_files):
        print(f"  ❌ {file.name}")


if __name__ == "__main__":
    asyncio.run(main())