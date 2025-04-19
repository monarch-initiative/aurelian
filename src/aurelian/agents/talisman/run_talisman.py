#!/usr/bin/env python3
"""
Standalone script to run the talisman agent directly.
"""
import os
import sys
from pydantic_ai import chat

# Add the src directory to the path for imports
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.insert(0, src_dir)

from aurelian.agents.talisman.talisman_agent import talisman_agent
from aurelian.agents.talisman.talisman_config import get_config

if __name__ == "__main__":
    config = get_config()
    chat(talisman_agent, deps=config)