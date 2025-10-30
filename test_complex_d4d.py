#!/usr/bin/env python3
"""
Test D4D agent with a more complex biomedical dataset.
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


# Create a D4D agent using Claude
claude_d4d_agent = Agent(
    model="anthropic:claude-3-5-sonnet-20241022",
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


async def test_complex_dataset():
    """Test the D4D agent with a complex biomedical dataset."""
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return
    
    # Configure the agent
    config = D4DConfig()
    
    # Complex biomedical dataset - PhysioNet MIMIC-CXR
    sample_url = "https://physionet.org/content/mimic-cxr/2.0.0/"
    
    print(f"Testing D4D agent with complex dataset: {sample_url}")
    print("This may take longer to process due to the complexity...")
    
    try:
        # Run the agent
        result = await claude_d4d_agent.run(
            f"Extract dataset metadata from: {sample_url}",
            deps=config
        )
        
        print("\n" + "="*50)
        print("EXTRACTED YAML METADATA:")
        print("="*50)
        print(result.output)
        
        # Save to file
        output_file = "mimic_cxr_d4d.yaml"
        with open(output_file, 'w') as f:
            f.write(result.output)
        print(f"\nSaved output to: {output_file}")
        
    except Exception as e:
        print(f"Error running D4D agent: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_complex_dataset())