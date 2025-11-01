"""
Tools for the D4D (Datasheets for Datasets) agent.
"""
import asyncio
import json
import tempfile
from pathlib import Path
from typing import Optional, Union

import requests
from pdfminer.high_level import extract_text
from pydantic_ai import RunContext, ModelRetry

from aurelian.utils.search_utils import retrieve_web_page as fetch_web_page
from .d4d_config import D4DConfig


async def get_full_schema(
    ctx: RunContext[D4DConfig],
    url: Optional[str] = None
) -> str:
    """
    Load the full datasheets for datasets schema from GitHub.
    
    Args:
        ctx: The run context
        url: Optional URL override for the schema location
        
    Returns:
        The schema text content
    """
    try:
        schema_url = url or ctx.deps.schema_url
        
        # Execute the potentially blocking operation in a thread pool
        def _fetch_schema():
            response = requests.get(schema_url)
            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"Failed to load schema: HTTP {response.status_code}")
                
        schema_text = await asyncio.to_thread(_fetch_schema)
        
        if not schema_text or schema_text.strip() == "":
            raise ModelRetry(f"Empty schema returned from URL: {schema_url}")
            
        return schema_text
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error loading schema: {str(e)}")


async def extract_text_from_pdf(
    ctx: RunContext[D4DConfig],
    pdf_url: str
) -> str:
    """
    Download and extract text from a PDF given its URL.
    
    Args:
        ctx: The run context
        pdf_url: The URL of the PDF to extract text from
        
    Returns:
        The extracted text content
    """
    try:
        # Execute the potentially blocking operation in a thread pool
        def _extract_pdf():
            response = requests.get(pdf_url)
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve PDF: HTTP {response.status_code}")
                
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
                temp_pdf.write(response.content)
                temp_pdf.flush()  # Ensure all data is written before reading
                
                text = extract_text(temp_pdf.name)
                if not text or text.strip() == "":
                    raise Exception("No text extracted from PDF")
                    
                return text.strip()
                
        pdf_text = await asyncio.to_thread(_extract_pdf)
        return pdf_text
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error extracting PDF text: {str(e)}")


async def retrieve_web_page(
    ctx: RunContext[D4DConfig],
    url: str
) -> str:
    """
    Retrieve the content of a web page.

    Args:
        ctx: The run context
        url: The URL of the web page to retrieve

    Returns:
        The web page content
    """
    try:
        # Execute the potentially blocking operation in a thread pool
        content = await asyncio.to_thread(fetch_web_page, url)

        if not content or content.strip() == "":
            raise ModelRetry(f"No content found for URL: {url}")

        return content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving web page: {str(e)}")


async def extract_text_from_html_file(
    ctx: RunContext[D4DConfig],
    file_path: Union[str, Path]
) -> str:
    """
    Read and extract text from a local HTML file.

    Args:
        ctx: The run context
        file_path: The path to the HTML file

    Returns:
        The HTML content as text
    """
    try:
        def _read_html():
            path = Path(file_path)
            if not path.exists():
                raise Exception(f"HTML file not found: {file_path}")

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content or content.strip() == "":
                raise Exception("HTML file is empty")

            # Truncate very long content to avoid token limits
            if len(content) > 50000:
                content = content[:50000] + "\n\n... [Content truncated for length] ..."

            return content

        html_content = await asyncio.to_thread(_read_html)
        return html_content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error reading HTML file: {str(e)}")


async def extract_text_from_json_file(
    ctx: RunContext[D4DConfig],
    file_path: Union[str, Path]
) -> str:
    """
    Read and extract text from a local JSON file.

    Args:
        ctx: The run context
        file_path: The path to the JSON file

    Returns:
        The JSON content as formatted text
    """
    try:
        def _read_json():
            path = Path(file_path)
            if not path.exists():
                raise Exception(f"JSON file not found: {file_path}")

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert to pretty-printed JSON string
            json_str = json.dumps(data, indent=2)

            if not json_str or json_str.strip() == "":
                raise Exception("JSON file is empty")

            # Truncate very long content to avoid token limits
            if len(json_str) > 50000:
                json_str = json_str[:50000] + "\n\n... [Content truncated for length] ..."

            return json_str

        json_content = await asyncio.to_thread(_read_json)
        return json_content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error reading JSON file: {str(e)}")


async def process_website_or_pdf(
    ctx: RunContext[D4DConfig],
    url_or_path: str
) -> str:
    """
    Determine if the input is a local file or URL, and process accordingly.
    Supports PDFs, HTML files, JSON files, and web pages.

    Args:
        ctx: The run context
        url_or_path: The URL or local file path of the content to process

    Returns:
        The extracted content from the file or web page
    """
    try:
        # Check if it's a local file path
        path = Path(url_or_path)
        is_local_file = path.exists()

        if is_local_file:
            # Handle local files based on extension
            suffix = path.suffix.lower()

            if suffix == '.pdf':
                # For local PDFs, we need to read and extract
                def _extract_local_pdf():
                    text = extract_text(str(path))
                    if not text or text.strip() == "":
                        raise Exception("No text extracted from PDF")
                    return text.strip()
                return await asyncio.to_thread(_extract_local_pdf)

            elif suffix == '.html' or suffix == '.htm':
                return await extract_text_from_html_file(ctx, path)

            elif suffix == '.json':
                return await extract_text_from_json_file(ctx, path)

            elif suffix == '.txt' or suffix == '.md':
                # Handle text and markdown files
                def _read_text():
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if len(content) > 50000:
                        content = content[:50000] + "\n\n... [Content truncated for length] ..."
                    return content
                return await asyncio.to_thread(_read_text)

            else:
                raise Exception(f"Unsupported file type: {suffix}")

        else:
            # Handle URLs
            is_pdf = False

            if url_or_path.lower().endswith(".pdf"):
                is_pdf = True
            else:
                # Check the content type in case the file doesn't have a .pdf extension
                def _check_content_type():
                    response = requests.head(url_or_path)
                    content_type = response.headers.get("Content-Type", "").lower()
                    return "pdf" in content_type

                is_pdf = await asyncio.to_thread(_check_content_type)

            # Retrieve the content based on the type
            if is_pdf:
                return await extract_text_from_pdf(ctx, url_or_path)
            else:
                return await retrieve_web_page(ctx, url_or_path)

    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error processing URL or file: {str(e)}")