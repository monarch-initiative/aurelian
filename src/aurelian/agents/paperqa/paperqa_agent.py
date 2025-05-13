"""
Agent for PaperQA integration with Aurelian.
"""
import logging
from pydantic_ai import Agent

paperqa_logger = logging.getLogger("aurelian.agents.paperqa")
paperqa_logger.setLevel(logging.INFO)

for handler in list(paperqa_logger.handlers):
    paperqa_logger.removeHandler(handler)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
paperqa_logger.addHandler(console)

paperqa_logger.propagate = False

from .paperqa_config import PaperQADependencies
from .paperqa_tools import (
    search_papers,
    query_papers,
    add_paper,
    add_papers,
    list_papers,
    build_index
)

PAPERQA_SYSTEM_PROMPT = """
        You are an AI assistant that helps explore scientific literature using PaperQA.
        You can use different functions to search for papers and analyze them:
          - `search_papers` to find papers by topic or keyword from outside this repository.
          - `query_papers` to ask questions about the papers in the repository
          - `add_paper` to add a specific paper by file path or URL (with auto_index=True by default)
          - `add_papers` to add multiple papers from a directory (with auto_index=True by default)
          - `list_papers` to see all papers in the collection
          - `build_index` to manually rebuild the search index
        
        When adding papers with `add_paper` or `add_papers`:
        - For `add_paper`, the URL must be a direct link to a PDF (e.g., "https://example.com/paper.pdf")
        - For `add_paper`, you can provide a citation string to attribute the source
        - For `add_papers`, you provide a directory containing papers and an optional citation format
        - By default, auto_index=True, which automatically rebuilds the index after adding papers
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
paperqa_agent.tool(add_papers)
paperqa_agent.tool(list_papers)
paperqa_agent.tool(build_index)
