#!/usr/bin/env python3
"""
Simple test script for the D4D agent.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import aurelian modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pydantic_ai import Agent
from aurelian.agents.d4d.d4d_config import D4DConfig
from aurelian.agents.d4d.d4d_tools import get_full_schema, process_website_or_pdf


# Create a D4D agent using Claude instead of OpenAI
claude_d4d_agent = Agent(
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


@claude_d4d_agent.system_prompt
async def add_schema(ctx) -> str:
    """Add the full schema to the system prompt."""
    schema = await get_full_schema(ctx)
    return schema


@claude_d4d_agent.tool
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


async def test_d4d_agent():
    """Test the D4D agent with a sample dataset."""
    
    # Check if we have an API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Configure the agent
    config = D4DConfig()
    
    # Sample dataset URL - using a simple dataset documentation page
    sample_url = "https://archive.ics.uci.edu/ml/datasets/iris"
    
    print(f"Testing D4D agent with URL: {sample_url}")
    print("This may take a moment to process...")
    
    try:
        # Run the agent
        result = await claude_d4d_agent.run(
            f"Extract dataset metadata from: {sample_url}",
            deps=config
        )
        
        print("\n" + "="*50)
        print("EXTRACTED YAML METADATA:")
        print("="*50)
        print(result.data)
        
    except Exception as e:
        print(f"Error running D4D agent: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_d4d_agent())