#!/usr/bin/env python3
"""
Main entry point to run the talisman agent.
"""
import os
import sys
from pydantic_ai import chat

# Add the parent directory to the path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from aurelian.agents.talisman.talisman_agent import talisman_agent
from aurelian.agents.talisman.talisman_config import get_config

if __name__ == "__main__":
    config = get_config()
    chat(talisman_agent, deps=config)