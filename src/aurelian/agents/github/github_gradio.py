"""
Gradio UI for the GitHub agent.
"""
from typing import List, Optional

import gradio as gr

from aurelian.dependencies.workdir import HasWorkdir
from aurelian.utils.async_utils import run_sync
from pydantic_ai import Agent, Tool
import aurelian.agents.github.github_tools as gt

# Create an Agent
github_agent = Agent(
    model="openai:gpt-4o",
    deps_type=HasWorkdir,
    system_prompt="""
    You are an expert GitHub assistant. You can help users interact with GitHub repositories,
    issues, pull requests, and more using the GitHub CLI (gh) and git commands.
    Always provide clear explanations of what you're doing.
    """,
    tools=[
        Tool(gt.list_issues),
        Tool(gt.get_issue_details),
        Tool(gt.list_pull_requests),
        Tool(gt.get_pull_request_details),
        Tool(gt.search_code),
        Tool(gt.get_repository_info),
    ]
)

def chat(deps: Optional[HasWorkdir] = None, **kwargs):
    """
    Initialize a chat interface for the GitHub agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = HasWorkdir()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: github_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="GitHub AI Assistant",
        examples=[
            ["List all open issues in this repository"],
            ["Show me pull request #42"],
            ["Search for code related to API authentication"],
            ["Get information about this repository"]
        ]
    )