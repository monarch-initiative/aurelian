"""
Agent for extracting dataset metadata following the datasheets for datasets schema.
"""
from typing import List

from pydantic_ai import Agent, RunContext

from .d4d_config import D4DConfig
from .d4d_tools import get_full_schema, process_website_or_pdf


# Create the agent, the full schema will be loaded when needed
d4d_agent = Agent(
    model="openai:gpt-4o",
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


@d4d_agent.system_prompt
async def add_schema(ctx: RunContext[D4DConfig]) -> str:
    """
    Add the full schema to the system prompt.

    Args:
        ctx: The run context

    Returns:
        The schema to be inserted into the system prompt
    """
    schema = await get_full_schema(ctx)
    return schema


@d4d_agent.tool
async def extract_metadata(ctx: RunContext[D4DConfig],
                           urls: List[str],
                           verbose: bool = True) -> str:
    """
    Extract metadata from a dataset description document or webpage.

    Args:
        ctx: The run context
        urls: The URLs of the dataset description (webpages or PDFs). There may be more than one.
        If there are multiple URLs, we will process each one separately and concatenate the content,
        then extract metadata from the combined content.
        verbose: If True, print message about the URLs being processed.

    Returns:
        YAML formatted metadata following the datasheets for datasets schema
    """
    # Retrieve the content
    content = ""
    for url in urls:
        import warnings
        if verbose:
            warnings.warn(f"Processing URL: {url}")
        content += await process_website_or_pdf(ctx, url)

    # Prepare a prompt to extract metadata
    prompt = f"""
The following is the content of one or more documents describing a dataset:

{content}

Using the complete datasheets for datasets schema provided above, extract all the metadata 
from the document and generate a YAML document that exactly conforms to that schema. 
"""

    # The prompt will be used as the user message
    return prompt
