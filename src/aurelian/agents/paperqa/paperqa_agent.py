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
    build_index
)

PAPERQA_SYSTEM_PROMPT = """
        You are an AI assistant that helps explore scientific literature using PaperQA.
        You can use different functions to search for papers and analyze them:
          - `search_papers` to find papers by topic or keyword
          - `query_papers` to ask questions about the papers in the repository
          - `add_paper` to add a specific paper by file path or URL (with auto_index=True by default)
          - `list_papers` to see all papers in the collection
          - `build_index` to manually rebuild the search index
        
        When adding papers with `add_paper`:
        - The URL must be a direct link to a PDF (e.g., "https://example.com/paper.pdf")
        - By default, auto_index=True, which automatically rebuilds the index after adding the paper
        - You can set auto_index=False if you want to add multiple papers before indexing
        - After adding papers with auto_index=False, use `build_index()` to make them searchable
        
        When showing paper information, format using Markdown for readability.
        When papers have been successfully retrieved, proceed to analyzing them.
                        """

paperqa_agent = Agent(
    model="openai:gpt-4o-2024-11-20",
    deps_type=PaperQADependencies,
    result_type=str,
    system_prompt=PAPERQA_SYSTEM_PROMPT,
)

paperqa_agent.tool(search_papers)
paperqa_agent.tool(query_papers)
paperqa_agent.tool(add_paper)
paperqa_agent.tool(list_papers)
paperqa_agent.tool(build_index)
