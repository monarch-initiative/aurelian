"""
Gradio UI for the GitHub agent.
"""
from typing import List, Optional
import tempfile
import os
import shutil

import gradio as gr

from aurelian.agents.github.github_config import GitHubDependencies
from aurelian.agents.github.github_agent import github_agent
from aurelian.utils.async_utils import run_sync
from aurelian.dependencies.workdir import WorkDir


def create_demo(workspace_dir: Optional[str] = None) -> gr.Blocks:
    """
    Create a Gradio demo for the GitHub agent.
    
    Args:
        workspace_dir: Directory to use as workspace. If None, a temporary directory is created.
        
    Returns:
        Gradio Blocks interface
    """
    temp_dir = None
    if workspace_dir is None:
        temp_dir = tempfile.mkdtemp()
        workspace_dir = temp_dir
    
    deps = GitHubDependencies()
    deps.workdir = WorkDir(location=workspace_dir)
    
    with gr.Blocks(title="GitHub Agent") as demo:
        gr.Markdown("# GitHub Repository Agent")
        gr.Markdown("""
        This agent helps you work with GitHub repositories, issues, and pull requests.
        
        You can:
        - List and view pull requests and issues
        - Find connections between PRs and issues
        - Search code in repositories
        - Clone repositories for deeper analysis
        - Examine commit history
        
        The agent uses the GitHub CLI, so you need to have it installed and authenticated.
        """)
        
        current_dir_md = gr.Markdown(f"**Working Directory**: {workspace_dir}")
        
        def update_current_dir():
            return f"**Working Directory**: {deps.workdir.location}"
        
        with gr.Row():
            with gr.Column():
                repo_input = gr.Textbox(label="Repository (owner/repo)")
                clone_btn = gr.Button("Clone Repository")
            
            with gr.Column():
                directory_input = gr.Textbox(label="Directory Name (optional)")
                branch_input = gr.Textbox(label="Branch (optional)")
        
        def clone_repo(repo: str, directory: Optional[str] = None, branch: Optional[str] = None):
            from aurelian.agents.github.github_tools import clone_repository
            from pydantic_ai import RunContext
            
            ctx = RunContext[GitHubDependencies](
                deps=deps, 
                model="openai:gpt-4o", 
                usage=None, 
                prompt=""
            )
            
            if not repo:
                return "Please enter a repository name in the format owner/repo", update_current_dir()
            
            try:
                clone_dir = clone_repository(ctx, repo, directory, branch)
                # Set workdir to the cloned repo
                deps.workdir = WorkDir(location=clone_dir)
                return f"Successfully cloned {repo} to {clone_dir}", update_current_dir()
            except Exception as e:
                return f"Error cloning repository: {str(e)}", update_current_dir()
        
        clone_result = gr.Textbox(label="Clone Result")
        clone_btn.click(clone_repo, inputs=[repo_input, directory_input, branch_input], outputs=[clone_result, current_dir_md])
        
        def get_info(query: str, history: List[List[str]]) -> str:
            flattened_history = []
            for h in history:
                flattened_history.extend(h)
            
            return run_sync(lambda: github_agent.chat(
                query, 
                deps=deps
            ).content)

        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="Your question about GitHub repositories")
        
        msg.submit(get_info, inputs=[msg, chatbot], outputs=chatbot)
        
        examples = [
            "List the most recent open pull requests",
            "What issues will be closed by PR #31?",
            "What was the commit before PR #31 was created?",
            "Search for code related to 'RunContext'",
            "Clone the repository 'obophenotype/cell-ontology' and list its files",
        ]
        gr.Examples(examples=examples, inputs=msg)
    
    # Cleanup temporary directory when demo is closed
    if temp_dir:
        def cleanup():
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        demo.close_callbacks.append(cleanup)
    
    return demo


def chat(deps: Optional[GitHubDependencies] = None, **kwargs):
    """
    Initialize a chat interface for the GitHub agent.
    
    Args:
        deps: Optional dependencies configuration
        **kwargs: Additional arguments to pass to the agent
        
    Returns:
        A Gradio chat interface
    """
    if deps is None:
        deps = GitHubDependencies()
        deps.workdir = WorkDir(location=os.getcwd())

    def get_info(query: str, history: List[str]) -> str:
        result = run_sync(lambda: github_agent.chat(query, deps=deps, **kwargs))
        return result.content

    return gr.ChatInterface(
        fn=get_info,
        title="GitHub AI Assistant",
        examples=[
            "List all open issues in monarch-initiative/aurelian",
            "Show me pull request #31 in monarch-initiative/aurelian",
            "Search for code related to RunContext in monarch-initiative/aurelian",
            "Get the commit before PR #31 was created"
        ]
    )