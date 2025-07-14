#!/usr/bin/env python3
"""Script to run only the MONDO evaluation dataset for the knowledge agent."""

import asyncio
from aurelian.agents.knowledge_agent.evals.mondo_evals import create_mondo_eval_dataset
from aurelian.agents.knowledge_agent.knowledge_agent_agent import knowledge_agent_agent
from aurelian.agents.knowledge_agent.knowledge_agent_config import get_config


async def main():
    """Run MONDO evaluations only."""
    dataset = create_mondo_eval_dataset()
    deps = get_config()
    
    async def run_agent(inputs: str):
        result = await knowledge_agent_agent.run(inputs, deps=deps)
        return result.data
    
    print("Running MONDO evaluation dataset...")
    report = await dataset.evaluate(run_agent)
    report.print(include_input=True, include_output=True)


if __name__ == "__main__":
    asyncio.run(main())