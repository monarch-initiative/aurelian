"""
Command-line interface for the GitHub agent.
"""
import os
import sys
import json
import click
import tempfile
import logging
from pathlib import Path
from typing import Optional

from aurelian.agents.github.github_agent import github_agent
from aurelian.agents.github.github_config import GitHubDependencies
from aurelian.dependencies.workdir import WorkDir


def setup_logging():
    """Set up logging for the CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def create_deps(workdir: Optional[str] = None) -> GitHubDependencies:
    """
    Create dependencies for the GitHub agent.
    
    Args:
        workdir: Working directory path. If None, uses current directory.
        
    Returns:
        GitHubDependencies instance
    """
    deps = GitHubDependencies()
    if workdir:
        wd_path = Path(workdir)
        # Create directory if it doesn't exist
        if not wd_path.exists():
            wd_path.mkdir(parents=True)
    else:
        workdir = os.getcwd()
    
    deps.workdir = WorkDir(location=workdir)
    return deps


@click.group()
@click.option('--workdir', '-w', help='Working directory path')
@click.pass_context
def cli(ctx, workdir):
    """GitHub repository assistant CLI."""
    setup_logging()
    ctx.obj = create_deps(workdir)


@cli.command()
@click.argument('repo')
@click.option('--directory', '-d', help='Directory name to clone into')
@click.option('--branch', '-b', help='Branch to clone')
@click.option('--depth', type=int, help='Depth limit for clone (for shallow clones)')
@click.pass_obj
def clone(deps, repo, directory, branch, depth):
    """Clone a GitHub repository."""
    from aurelian.agents.github.github_tools import clone_repository
    from pydantic_ai import RunContext
    
    ctx = RunContext[GitHubDependencies](deps=deps, model="openai:gpt-4o", usage=None, prompt="")
    
    try:
        clone_dir = clone_repository(ctx, repo, directory, branch, depth)
        click.echo(f"Successfully cloned {repo} to {clone_dir}")
        
        # Optionally update workdir to the cloned repo
        if click.confirm("Do you want to set the working directory to the cloned repository?"):
            deps.workdir = WorkDir(location=clone_dir)
            click.echo(f"Working directory updated to: {clone_dir}")
    except Exception as e:
        click.echo(f"Error cloning repository: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--state', '-s', default='open', help='Filter by state (open, closed, merged, all)')
@click.option('--limit', '-l', default=10, type=int, help='Maximum number of PRs to return')
@click.option('--label', help='Filter by label')
@click.option('--author', '-a', help='Filter by author')
@click.option('--base', help='Filter by base branch')
@click.option('--repo', '-r', help='Repository (format: owner/repo)')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', 'format_', type=click.Choice(['pretty', 'json']), default='pretty', 
              help='Output format (pretty or json)')
@click.pass_obj
def list_prs(deps, state, limit, label, author, base, repo, output, format_):
    """List pull requests from GitHub."""
    from aurelian.agents.github.github_tools import list_pull_requests
    from pydantic_ai import RunContext
    
    ctx = RunContext[GitHubDependencies](deps=deps, model="openai:gpt-4o", usage=None, prompt="")
    
    try:
        results = list_pull_requests(ctx, state, limit, label, author, base, repo)
        
        if format_ == 'json':
            output_data = json.dumps(results, indent=2)
        else:
            output_data = "Pull Requests:\n"
            for i, pr in enumerate(results, 1):
                output_data += f"{i}. #{pr['number']} - {pr['title']} ({pr['state']})\n"
                output_data += f"   Author: {pr['author']['login']}\n"
                output_data += f"   Created: {pr['createdAt']}\n"
                output_data += f"   URL: {pr['url']}\n\n"
        
        if output:
            with open(output, 'w') as f:
                f.write(output_data)
            click.echo(f"Results written to {output}")
        else:
            click.echo(output_data)
    except Exception as e:
        click.echo(f"Error listing pull requests: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('pr_number')
@click.option('--repo', '-r', help='Repository (format: owner/repo)')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', 'format_', type=click.Choice(['pretty', 'json']), default='pretty',
              help='Output format (pretty or json)')
@click.pass_obj
def view_pr(deps, pr_number, repo, output, format_):
    """View a specific pull request."""
    from aurelian.agents.github.github_tools import view_pull_request
    from pydantic_ai import RunContext
    
    ctx = RunContext[GitHubDependencies](deps=deps, model="openai:gpt-4o", usage=None, prompt="")
    
    try:
        result = view_pull_request(ctx, pr_number, repo)
        
        if format_ == 'json':
            output_data = json.dumps(result, indent=2)
        else:
            output_data = f"PR #{result['number']}: {result['title']}\n"
            output_data += f"State: {result['state']}\n"
            output_data += f"Author: {result['author']['login']}\n"
            output_data += f"Created: {result['createdAt']}\n"
            output_data += f"URL: {result['url']}\n"
            output_data += f"Base: {result['baseRefName']} <- Head: {result['headRefName']}\n\n"
            output_data += f"Description:\n{result['body']}\n\n"
            
            if result.get('closingIssues'):
                output_data += "Closes Issues:\n"
                for issue in result['closingIssues']:
                    output_data += f"- #{issue['number']}: {issue['title']}\n"
        
        if output:
            with open(output, 'w') as f:
                f.write(output_data)
            click.echo(f"Results written to {output}")
        else:
            click.echo(output_data)
    except Exception as e:
        click.echo(f"Error viewing pull request: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('pr_number')
@click.option('--repo', '-r', help='Repository (format: owner/repo)')
@click.pass_obj
def commit_before_pr(deps, pr_number, repo):
    """Get the commit before a PR branch was created."""
    from aurelian.agents.github.github_tools import get_commit_before_pr
    from pydantic_ai import RunContext
    
    ctx = RunContext[GitHubDependencies](deps=deps, model="openai:gpt-4o", usage=None, prompt="")
    
    try:
        result = get_commit_before_pr(ctx, pr_number, repo)
        click.echo(f"Commit before PR #{pr_number} was created:")
        click.echo(f"Hash: {result['hash']}")
        click.echo(f"Message:\n{result['message']}")
    except Exception as e:
        click.echo(f"Error getting commit before PR: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--repo', '-r', help='Repository (format: owner/repo)')
@click.option('--output', '-o', help='Output file path')
@click.pass_obj
def search(deps, query, repo, output):
    """Search for code in a repository."""
    from aurelian.agents.github.github_tools import search_code
    from pydantic_ai import RunContext
    
    ctx = RunContext[GitHubDependencies](deps=deps, model="openai:gpt-4o", usage=None, prompt="")
    
    try:
        results = search_code(ctx, query, repo)
        
        output_data = f"Search results for: {query}\n\n"
        for i, match in enumerate(results, 1):
            output_data += f"{i}. {match['path']}\n"
            for text_match in match.get('textMatches', []):
                if 'fragment' in text_match:
                    output_data += f"   ...{text_match['fragment']}...\n"
            output_data += "\n"
        
        if output:
            with open(output, 'w') as f:
                f.write(output_data)
            click.echo(f"Results written to {output}")
        else:
            click.echo(output_data)
    except Exception as e:
        click.echo(f"Error searching code: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--query', '-q', help='Initial question or prompt for the agent')
@click.pass_obj
def chat(deps, query):
    """Start an interactive chat with the GitHub agent."""
    click.echo("Starting chat with GitHub agent. Type 'exit' or 'quit' to end.")
    
    if query:
        response = github_agent.chat(query, deps=deps)
        click.echo(f"Agent: {response.content}")
    
    while True:
        user_input = click.prompt("You", type=str)
        if user_input.lower() in ('exit', 'quit'):
            click.echo("Exiting chat.")
            break
        
        response = github_agent.chat(user_input, deps=deps)
        click.echo(f"Agent: {response.content}")


if __name__ == '__main__':
    cli()