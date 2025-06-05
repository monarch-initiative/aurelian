"""Knowledge Agent for scientific knowledge extraction."""

from typing import Any

from pydantic_ai import Agent
from ruamel.yaml import YAML

from aurelian.agents.knowledge_agent.knowledge_agent_config import KnowledgeAgentDependencies
from aurelian.agents.knowledge_agent.knowledge_agent_tools import search_ontology_with_oak


def knowledge_agent(model="openai:gpt-4o", deps=None):
    """Initialize the Knowledge Agent.

    Args:
        model: The model to use for the agent
        deps: Dependencies for the agent

    Returns:
        Agent: A configured knowledge agent
    """
    return Agent(
        model,
        system_prompt="""
        You are an expert curator of scientific knowledge. Your purpose is to take 
        unstructured scientific text and output structured scientific knowledge that is 
        aligned to a schema that describes the knowledge the user wants to extract.  

        You will be given some scientific text and a schema in LinkML format, and you 
        will output the knowledge contained in the scientific text such that it aligns
        with the LinkML schema. 

        You can output as much or as little data as you think is sensible, as long as it is
        supported by the scientific text. 

        The LinkML schema describes the knowledge that the user wants to extract. Pay particular
        attention to entity types and relationships defined in the schema. These describe
        the types of things the user is interested in, and relationships between them.

        The schema may include some advice about what annotators to use when using the 
        search_ontology tool to ground the terms to the schema. For example, the following items
        in the schema mean that you should use the Mondo Disease Ontology to ground disease 
        terms:

        id_prefixes:
          - MONDO
        annotations:
          annotators: sqlite:obo:mondo

        and the following means that you should use the Human Phenotype Ontology: 

        id_prefixes:
        - HP
        annotations:
          annotators: sqlite:obo:hp

        Some other guidelines:
        1. Use the schema to guide your extraction of knowledge from the scientific text.
        2. Do not respond conversationally, but rather output the structured knowledge without
        any additional commentary.
        """,
        tools=[search_ontology_with_oak]
    )


def run_sync(prompt: str, deps: KnowledgeAgentDependencies = None, **kwargs) -> Any:
    """Run the Knowledge Agent synchronously.

    Args:
        prompt: The prompt to send to the agent
        deps: Dependencies for the agent
        **kwargs: Additional arguments to pass to the agent

    Returns:
        Any: The result from running the agent
    """
    agent = knowledge_agent(model=kwargs.get("model", "openai:gpt-4o"), deps=deps)
    return agent.run_sync(user_prompt=prompt)
