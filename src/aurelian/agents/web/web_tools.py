from typing import List, Optional
import os
import xml.etree.ElementTree as ET
from pydantic import BaseModel, Field

from aurelian.utils.search_utils import web_search
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


class Citation(BaseModel):
    """Citation model for query results with citations."""
    
    citation_number: str = Field(description="Citation number or identifier")
    url: str = Field(description="URL source of the citation") 
    timestamp: Optional[str] = Field(
        default=None, description="Timestamp of the citation, if available"
    )


class ResultWithCitations(BaseModel):
    """Generic result model for queries that return content with citations."""
    
    content: str = Field(description="Content of the response")
    citations: List[Citation] = Field(
        default_factory=list, description="List of citations referenced in the content"
    )


async def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Args:
        query: Text query

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)


async def perplexity_query(query: str, model_name: str = "sonar") -> ResultWithCitations:
    """
    Query the Perplexity API and return structured results with citations.
    
    Args:
        query: The query to send to Perplexity
        model_name: The Perplexity model to use (default: "sonar"). Options include "sonar", "sonar-pro", etc.
        
    Returns:
        ResultWithCitations: A structured response with content and citations
        
    Raises:
        ValueError: If the Perplexity API key is not set
        RuntimeError: If the response parsing fails
    """
    perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not perplexity_api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable is not set")
        
    sonar_model = OpenAIModel(
        model_name=model_name,
        base_url='https://api.perplexity.ai',
        api_key=perplexity_api_key,
    )
    
    agent = Agent(sonar_model,
                  system_prompt=("Return the response with xml tags <answer> and <citations>,"
                                 "where citations includes a list with the citation_number, url,"
                                 " and timestamp for the retrieved citations"))
    result = agent.run_sync(query)
    
    try:
        # Parse the XML response
        xml_string = f"<root>{result.data}</root>"
        root = ET.fromstring(xml_string)
        
        # Extract answer content
        answer_element = root.find("answer")
        content = answer_element.text.strip() if answer_element is not None and answer_element.text else ""
        
        # Extract citations
        citations_list = []
        citations_element = root.find("citations")
        if citations_element is not None:
            for citation in citations_element.findall(".//citation"):
                citation_number = citation.find("citation_number")
                if citation_number is None:
                    citation_number = citation.find("number")
                
                url_element = citation.find("url")
                timestamp_element = citation.find("timestamp")
                
                citations_list.append(
                    Citation(
                        citation_number=citation_number.text if citation_number is not None and citation_number.text else "",
                        url=url_element.text if url_element is not None and url_element.text else "",
                        timestamp=timestamp_element.text if timestamp_element is not None and timestamp_element.text else None
                    )
                )
        
        return ResultWithCitations(content=content, citations=citations_list)
    except ET.ParseError as e:
        raise RuntimeError(f"Failed to parse Perplexity response: {e}")
