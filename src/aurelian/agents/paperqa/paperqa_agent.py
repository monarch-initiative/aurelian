"""
Agent for PaperQA integration with Aurelian.
"""
from pydantic_ai import Agent, RunContext

from .paperqa_config import PaperQADependencies, get_config
from .paperqa_tools import (
    search_papers,
    query_papers,
    add_paper,
    list_papers,
)

# Create the PaperQA agent
paperqa_agent = Agent(
    model="openai:gpt-4o",
    deps_type=PaperQADependencies,
    result_type=str,
    system_prompt=(
        "You are an AI assistant that helps explore scientific literature using PaperQA. "
        "You can use different functions to search for papers and analyze them:"
        "  - `search_papers` to find papers by topic or keyword"
        "  - `query_papers` to ask questions about the papers in the repository"
        "  - `add_paper` to add a specific paper by file path or URL"
        "  - `list_papers` to see all papers in the collection"
        "When showing paper information, format using Markdown for readability."
        "When papers have been successfully retrieved, proceed to analyzing them."
    ),
)

paperqa_agent.tool(search_papers)
paperqa_agent.tool(query_papers)
paperqa_agent.tool(add_paper)
paperqa_agent.tool(list_papers)
