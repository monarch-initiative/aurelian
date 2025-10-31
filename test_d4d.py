#!/usr/bin/env python3
"""
Simple test script for the D4D agent.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import aurelian modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aurelian.agents.d4d.d4d_config import D4DConfig
from aurelian.agents.d4d.d4d_agent import d4d_agent


async def test_d4d_agent():
    """Test the D4D agent with a sample dataset."""

    # Check if we have an API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return

    # Configure the agent
    config = D4DConfig()

    # Sample dataset URL - using a simple dataset documentation page
    sample_url = "https://archive.ics.uci.edu/ml/datasets/iris"

    print(f"Testing D4D agent with URL: {sample_url}")
    print("This may take a moment to process...")

    try:
        # Run the agent using the canonical d4d_agent
        result = await d4d_agent.run(
            f"Extract dataset metadata from: {sample_url}",
            deps=config
        )

        print("\n" + "="*50)
        print("EXTRACTED YAML METADATA:")
        print("="*50)
        print(result.data)

    except Exception as e:
        print(f"Error running D4D agent: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_d4d_agent())