"""Command line interface for Aurelian agents."""

import logging
import os
from typing import Any, Awaitable, Callable, Optional, List

import click
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from aurelian import __version__

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)


def parse_multivalued(ctx, param, value: Optional[str]) -> Optional[List]:
    """Parse a comma-separated string into a list."""
    if not value:
        return None
    return value.split(',') if isinstance(value, str) and ',' in value else [value]


# Common CLI options
model_option = click.option(
    "--model",
    "-m",
    help="The model to use for the agent.",
)
use_cborg_option = click.option(
    "--use-cborg/--no-use-cborg",
    default=False,
    show_default=True,
    help="Use CBORG as a model proxy (LBNL account required).",
)
agent_option = click.option(
    "--agent",
    "-a",
    help="The agent to use (if non-default).",
)
workdir_option = click.option(
    "--workdir",
    "-w",
    default="workdir",
    show_default=True,
    help="The working directory for the agent.",
)
share_option = click.option(
    "--share/--no-share",
    default=False,
    show_default=True,
    help="Share the agent GradIO UI via URL.",
)
ui_option = click.option(
    "--ui/--no-ui",
    default=False,
    show_default=True,
    help="Start the agent in UI mode instead of direct query mode.",
)
run_evals_option = click.option(
    "--run-evals/--no-run-evals",
    default=False,
    show_default=True,
    help="Run the agent in evaluation mode.",
)
ontologies_option = click.option(
    "--ontologies",
    "-i",
    callback=parse_multivalued,
    help="Comma-separated list of ontologies to use for the agent.",
)
server_port_option = click.option(
    "--server-port",
    "-p",
    default=7860,
    show_default=True,
    help="The port to run the UI server on.",
)
db_path_option = click.option(
    "--db-path",
    "-d",
    help="The path to the database.",
)
collection_name_option = click.option(
    "--collection-name",
    "-c",
    help="The name of the collection.",
)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """Main command for Aurelian.

    Aurelian provides a collection of specialized agents for various scientific and biomedical tasks.
    Each agent can be run in either direct query mode or UI mode:
    
    - Direct query mode: Run the agent with a query (e.g., `aurelian diagnosis "patient with hypotonia"`).
    - UI mode: Run the agent with `--ui` flag to start a chat interface.
    
    Some agents also provide utility commands for specific operations.

    :param verbose: Verbosity while running.
    :param quiet: Boolean to be quiet or verbose.
    """
    if verbose >= 2:
        logger.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(level=logging.INFO)
    else:
        logger.setLevel(level=logging.WARNING)
    if quiet:
        logger.setLevel(level=logging.ERROR)
    import logfire

    logfire.configure()


def split_options(kwargs, agent_keys: Optional[List]=None, extra_agent_keys: Optional[List] = None):
    """Split options into agent and launch options."""
    if agent_keys is None:
        agent_keys = ["model", "workdir", "ontologies", "db_path", "collection_name"]
    if extra_agent_keys is not None:
        agent_keys += extra_agent_keys
    agent_options = {k: v for k, v in kwargs.items() if k in agent_keys}
    launch_options = {k: v for k, v in kwargs.items() if k not in agent_keys}
    return agent_options, launch_options


def run_agent(
    agent_name: str, 
    agent_module: str, 
    query: Optional[tuple] = None, 
    ui: bool = False,
    specialist_agent_name: Optional[str] = None,
    agent_func_name: str = "run_sync",
    join_char: str = " ",
    use_cborg: bool = False,
    **kwargs
) -> None:
    """Run an agent in either UI or direct query mode.
    
    Args:
        agent_name: Agent's name for import paths
        agent_module: Fully qualified module path to the agent
        query: Text query for direct mode
        ui: Whether to force UI mode
        specialist_agent_name: Name of the agent class to run
        agent_func_name: Name of the function to run the agent
        join_char: Character to join multi-part queries with
        kwargs: Additional arguments for the agent
    """
    # DEPRECATED: use the new agent command instead
    # Import required modules
    # These are imported dynamically to avoid loading all agents on startup
    if not agent_module:
        agent_module = f"aurelian.agents.{agent_name}"
    if not specialist_agent_name:
        specialist_agent_name = agent_name
    gradio_module = __import__(f"{agent_module}.{agent_name}_gradio", fromlist=["chat"])
    agent_class = __import__(f"{agent_module}.{agent_name}_agent", fromlist=[f"{specialist_agent_name}_agent"])
    config_module = __import__(f"{agent_module}.{agent_name}_config", fromlist=["get_config"])
    
    chat_func = gradio_module.chat
    agent = getattr(agent_class, f"{specialist_agent_name}_agent")
    get_config = config_module.get_config
    
    # Process agent and UI options
    agent_keys = ["model", "use_cborg", "workdir", "ontologies", "db_path", "collection_name"]
    agent_options, launch_options = split_options(kwargs, agent_keys=agent_keys)

    deps = get_config()

    # Set workdir if provided
    if 'workdir' in agent_options and agent_options['workdir']:
        if hasattr(deps, 'workdir'):
            deps.workdir.location = agent_options['workdir']

    # Remove workdir from agent options to avoid duplicates
    agent_run_options = {k: v for k, v in agent_options.items() if k != 'workdir'}

    if use_cborg:
        cborg_api_key = os.environ.get("CBORG_API_KEY")
        model = OpenAIModel(
            agent_run_options.get("model", kwargs.get("model", "openai:gpt-4o")),
            provider=OpenAIProvider(
                base_url="https://api.cborg.lbl.gov",
                api_key=cborg_api_key),
        )
        print(f"CBORG model: {model}")
        agent_run_options["model"] = model

    # Run in appropriate mode
    if not ui and query:
        # Direct query mode
        
        # Run the agent and print results
        agent_run_func = getattr(agent, agent_func_name)
        r = agent_run_func(join_char.join(query), deps=deps, **agent_run_options)
        print(r.data)
        mjb = r.all_messages_json()
        # decode messages from json bytes to dict:
        if isinstance(mjb, bytes):
            mjb = mjb.decode()
        # print the messages
        import json
        all_messages = json.loads(mjb)
        import yaml
        # print(yaml.dump(all_messages, indent=2))
    else:
        print(f"Running {agent_name} in UI mode, agent options: {agent_options}")
        # UI mode
        gradio_ui = chat_func(deps=deps, **agent_run_options)
        gradio_ui.launch(**launch_options)


@main.command()
@agent_option
@model_option
@use_cborg_option
@share_option
@server_port_option
@workdir_option
@ui_option  
@run_evals_option
@click.argument("query", nargs=-1, required=False)
def agent(ui, query, agent, use_cborg=False, run_evals=False, **kwargs):
    """NEW: Generic agent runner.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    if not agent:
        raise click.UsageError("Error: --agent is required")
    agent_module = f"aurelian.agents.{agent}"
    specialist_agent_name = agent
    gradio_module = __import__(f"{agent_module}.{agent}_gradio", fromlist=["chat"])
    agent_class = __import__(f"{agent_module}.{agent}_agent", fromlist=[f"{specialist_agent_name}_agent"])
    config_module = __import__(f"{agent_module}.{agent}_config", fromlist=["get_config"])
    
    chat_func = gradio_module.chat
    agent_obj = getattr(agent_class, f"{specialist_agent_name}_agent")
    get_config = config_module.get_config
    
    # Process agent and UI options
    agent_keys = ["model", "use_cborg", "workdir", "ontologies", "db_path", "collection_name"]
    agent_options, launch_options = split_options(kwargs, agent_keys=agent_keys)

    deps = get_config()

    # Set workdir if provided
    if hasattr(deps, 'workdir'):
        deps.workdir.location = kwargs['workdir']

    # Remove workdir from agent options to avoid duplicates
    agent_run_options = {k: v for k, v in agent_options.items() if k != 'workdir'}

    # TODO: make this generic, for any proxy model
    if use_cborg:
        cborg_api_key = os.environ.get("CBORG_API_KEY")
        model = OpenAIModel(
            agent_run_options.get("model", "openai:gpt-4o"),
            provider=OpenAIProvider(
                base_url="https://api.cborg.lbl.gov",
                api_key=cborg_api_key),
        )
        agent_run_options["model"] = model

    # Run in appropriate mode
    if not ui and query:
        # Direct query mode
        join_char = " "
        # Run the agent and print results
        agent_run_func = getattr(agent_obj, "run_sync")
        r = agent_run_func(join_char.join(query), deps=deps, **agent_run_options)
        print(r.data)
        mjb = r.all_messages_json()
        # decode messages from json bytes to dict:
        if isinstance(mjb, bytes):
            mjb = mjb.decode()
        # print the messages
        import json
        all_messages = json.loads(mjb)
        import yaml
        # print(yaml.dump(all_messages, indent=2))
    elif run_evals:
        import sys
        import importlib
        # TODO: make this generic
        package_name = f"{agent_module}.{agent}_evals"
        module = importlib.import_module(package_name)
        dataset = module.create_eval_dataset()

        async def run_agent(inputs: str) -> Any:
            result = await agent_obj.run(inputs, deps=deps, **agent_run_options)
            return result.data
        
        eval_func: Callable[[str], Awaitable[str]] = run_agent
        report = dataset.evaluate_sync(eval_func)
        report.print(include_input=True, include_output=True)
    else:
        print(f"Running {agent} in UI mode, agent options: {agent_options}")
        # UI mode
        gradio_ui = chat_func(deps=deps, **agent_run_options)
        gradio_ui.launch(**launch_options)



@main.command()
@click.option("--limit", "-l", default=10, show_default=True, help="Number of results to return.")
@click.argument("ontology")
@click.argument("term")
def search_ontology(ontology: str, term: str, **kwargs):
    """Search the ontology for the given query term.

    Also has side effect of indexing. You may want to pre-index before
    starting an individual UI.
    """
    import aurelian.utils.ontology_utils as ontology_utils
    from oaklib import get_adapter

    handle = "sqlite:obo:" + ontology
    adapter = get_adapter(handle)
    objs = ontology_utils.search_ontology(adapter, term, **kwargs)
    for id, label in objs:
        print(id, label)


@main.command()
@agent_option
@model_option
@use_cborg_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def gocam(ui, query, agent, **kwargs):
    """Start the GO-CAM Agent for gene ontology causal activity models.
    
    The GO-CAM Agent helps create and analyze Gene Ontology Causal Activity Models,
    which describe biological systems as molecular activities connected by causal 
    relationships. 
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("gocam", "aurelian.agents.gocam", query=query, ui=ui, specialist_agent_name=agent, **kwargs)



@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def phenopackets(ui, query, **kwargs):
    """Start the Phenopackets Agent for standardized phenotype data.
    
    The Phenopackets Agent helps work with GA4GH Phenopackets, a standard 
    format for sharing disease and phenotype information for genomic 
    medicine.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("phenopackets", "aurelian.agents.phenopackets", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def diagnosis(ui, query, **kwargs):
    """Start the Diagnosis Agent for rare disease diagnosis.
    
    The Diagnosis Agent assists in diagnosing rare diseases by leveraging the 
    Monarch Knowledge Base. It helps clinical geneticists evaluate potential 
    conditions based on patient phenotypes.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("diagnosis", "aurelian.agents.diagnosis", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def checklist(ui, query, **kwargs):
    """Start the Checklist Agent for paper evaluation.
    
    The Checklist Agent evaluates scientific papers against established checklists 
    such as STREAMS, STORMS, and ARRIVE. It helps ensure that papers conform to 
    relevant reporting guidelines and best practices.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("checklist", "aurelian.agents.checklist", query=query, ui=ui, **kwargs)


# Keep backward compatibility
@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
def aria(**kwargs):
    """Start the Checklist UI (deprecated, use 'checklist' instead)."""
    run_agent("checklist", "aurelian.agents.checklist", ui=True, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def linkml(ui, query, **kwargs):
    """Start the LinkML Agent for data modeling and schema validation.
    
    The LinkML Agent helps create and validate data models and schemas using the 
    Linked data Modeling Language (LinkML). It can assist in generating schemas,
    validating data against schemas, and modeling domain knowledge.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("linkml", "aurelian.agents.linkml", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def robot(ui, query, **kwargs):
    """Start the ROBOT Agent for ontology operations.
    
    The ROBOT Agent provides natural language access to ontology operations 
    and manipulations using the ROBOT tool. It can create, modify, and analyze
    ontologies through a chat interface.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("robot", "aurelian.agents.robot", query=query, ui=ui, agent_func_name="chat", **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def amigo(ui, query, **kwargs):
    """Start the AmiGO Agent for Gene Ontology data exploration.
    
    The AmiGO Agent provides access to the Gene Ontology (GO) and gene 
    product annotations. It helps users explore gene functions and 
    ontology relationships.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("amigo", "aurelian.agents.amigo", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@db_path_option
@collection_name_option
@click.argument("query", nargs=-1, required=False)
def rag(ui, query, db_path, collection_name, **kwargs):
    """Start the RAG Agent for document retrieval and generation.
    
    The RAG (Retrieval-Augmented Generation) Agent provides a natural language 
    interface for exploring and searching document collections. It uses RAG 
    techniques to combine search capabilities with generative AI.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    if not db_path:
        click.echo("Error: --db-path is required")
        return
    
    # Add special parameters to kwargs
    kwargs["db_path"] = db_path
    if collection_name:
        kwargs["collection_name"] = collection_name
        
    run_agent("rag", "aurelian.agents.rag", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@ontologies_option
@click.argument("query", nargs=-1, required=False)
def mapper(ui, query, ontologies, **kwargs):
    """Start the Ontology Mapper Agent for mapping between ontologies.
    
    The Ontology Mapper Agent helps translate terms between different ontologies
    and vocabularies. It can find equivalent concepts across ontologies and 
    explain relationships.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    # Special handling for ontologies parameter
    if ontologies:
        if isinstance(ontologies, str):
            ontologies = [ontologies]
        kwargs["ontologies"] = ontologies
        
    run_agent("ontology_mapper", "aurelian.agents.ontology_mapper", query=query, ui=ui, join_char="\n", **kwargs)


@main.command()
@click.argument("pmid")
def fulltext(pmid):
    """Download full text for a PubMed article."""
    from aurelian.utils.pubmed_utils import get_pmid_text
    txt = get_pmid_text(pmid)
    print(txt)


@main.command()
@click.argument("term")
def websearch(term):
    """Search the web for a query term."""
    from aurelian.utils.search_utils import web_search
    txt = web_search(term)
    print(txt)


@main.command()
@click.argument("url")
def geturl(url):
    """Retrieve content from a URL."""
    from aurelian.utils.search_utils import retrieve_web_page
    txt = retrieve_web_page(url)
    print(txt)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("url", required=False)
def datasheets(ui, url, **kwargs):
    """Start the Datasheets for Datasets (D4D) Agent.
    
    The D4D Agent extracts structured metadata from dataset documentation
    according to the Datasheets for Datasets schema. It can analyze both 
    web pages and PDF documents describing datasets.
    
    Run with a URL for direct mode or with --ui for interactive chat mode.
    """
    run_agent("d4d", "aurelian.agents.d4d", query=(url,) if url else None, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def chemistry(ui, query, **kwargs):
    """Start the Chemistry Agent for chemical structure analysis.
    
    The Chemistry Agent helps interpret and work with chemical structures,
    formulas, and related information.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("chemistry", "aurelian.agents.chemistry", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def literature(ui, query, **kwargs):
    """Start the Literature Agent for scientific publication analysis.
    
    The Literature Agent provides tools for analyzing scientific publications,
    extracting key information, and answering questions about research articles.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("literature", "aurelian.agents.literature", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def biblio(ui, query, **kwargs):
    """Start the Biblio Agent for bibliographic data management.
    
    The Biblio Agent helps organize and search bibliographic data and citations. 
    It provides tools for searching a bibliography database, retrieving scientific 
    publications, and accessing web content.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("biblio", "aurelian.agents.biblio", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def monarch(ui, query, **kwargs):
    """Start the Monarch Agent for biomedical knowledge exploration.
    
    The Monarch Agent provides access to relationships between genes, diseases, 
    phenotypes, and other biomedical entities through the Monarch Knowledge Base.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("monarch", "aurelian.agents.monarch", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def ubergraph(ui, query, **kwargs):
    """Start the UberGraph Agent for SPARQL-based ontology queries.
    
    The UberGraph Agent provides a natural language interface to query ontologies 
    using SPARQL through the UberGraph endpoint. It helps users formulate and execute
    SPARQL queries without needing to know the full SPARQL syntax.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("ubergraph", "aurelian.agents.ubergraph", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def gene(ui, query, **kwargs):
    """Start the Gene Agent for retrieving gene descriptions.
    
    The Gene Agent retrieves descriptions for gene identifiers using the UniProt API.
    It can process a single gene or a list of genes and returns detailed information
    about gene function, products, and associations.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("gene", "aurelian.agents.gene", query=query, ui=ui, **kwargs)

@main.command()
@model_option
@use_cborg_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def goann(ui, query, **kwargs):
    """Start the GO Annotation Review Agent for evaluating GO annotations.
    
    The GO Annotation Review Agent helps review GO annotations for accuracy 
    and proper evidence. It can evaluate annotations based on evidence codes,
    identify potential over-annotations, and ensure compliance with GO guidelines,
    particularly for transcription factors.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("goann", "aurelian.agents.goann", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def github(ui, query, **kwargs):
    """Start the GitHub Agent for repository interaction.
    
    The GitHub Agent provides a natural language interface for interacting with GitHub
    repositories. It can list/view pull requests and issues, find connections between PRs 
    and issues, search code, clone repositories, and examine commit history.
    
    Requires GitHub CLI (gh) to be installed and authenticated.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("github", "aurelian.agents.github", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def draw(ui, query, **kwargs):
    """Start the Draw Agent for creating SVG drawings.
    
    The Draw Agent creates SVG drawings based on text descriptions and provides 
    feedback on drawing quality from an art critic judge. It helps generate visual 
    representations from textual descriptions with a focus on clarity and simplicity.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("draw", "aurelian.agents.draw", query=query, ui=ui, **kwargs)


@main.command()
@ui_option
@workdir_option
@share_option
@server_port_option
@click.argument("query", nargs=-1, required=False)
def talisman(ui, query, **kwargs):
    """Start the Talisman Agent for advanced gene analysis.
    
    The Talisman Agent retrieves descriptions for gene identifiers using UniProt and NCBI Entrez.
    It can process a single gene, protein ID, or a list of genes and returns detailed information.
    It also can analyze relationships between multiple genes to identify functional connections.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    
    Examples:
        aurelian talisman TP53
        aurelian talisman "TP53, MDM2"
        aurelian talisman "BRCA1, BRCA2, ATM, PARP1"
    """
    run_agent("talisman", "aurelian.agents.talisman", query=query, ui=ui, **kwargs)
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def reaction(ui, query, **kwargs):
    """Start the Reaction Agent for biochemical reaction query and curation.
    
    The Reaction Agent helps query and curate biochemical reactions from various sources
    including RHEA and UniProt. It can identify enzymes, substrates, products, and 
    extract reaction information from scientific text.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("reaction", "aurelian.agents.reaction", query=query, ui=ui, **kwargs)



# DO NOT REMOVE THIS LINE
# added this for mkdocstrings to work
# see https://github.com/bruce-szalwinski/mkdocs-typer/issues/18
#click_app = get_command(app)
#click_app.name = "aurelian"

if __name__ == "__main__":
    main()
