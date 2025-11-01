#!/usr/bin/env python3
"""
Demo script showing how to use the D4D agent.
This demonstrates the agent setup without requiring an API key.
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import aurelian modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aurelian.agents.d4d.d4d_config import D4DConfig
from aurelian.agents.d4d.d4d_tools import get_full_schema, process_website_or_pdf


async def demo_d4d_functionality():
    """Demo the D4D agent functionality without running the full agent."""
    
    print("D4D Agent Demo")
    print("=" * 40)
    
    # Configure the agent
    config = D4DConfig()
    print(f"Schema URL: {config.schema_url}")
    
    # Test loading the schema
    try:
        print("\n1. Loading D4D schema...")
        schema = await get_full_schema(None, config.schema_url)
        schema_lines = schema.split('\n')
        print(f"Schema loaded successfully! ({len(schema_lines)} lines)")
        print("First 10 lines of schema:")
        for i, line in enumerate(schema_lines[:10]):
            print(f"  {i+1}: {line}")
        if len(schema_lines) > 10:
            print(f"  ... and {len(schema_lines) - 10} more lines")
            
    except Exception as e:
        print(f"Error loading schema: {e}")
        return
    
    # Test URL processing (but don't actually fetch to avoid needing API key)
    print(f"\n2. D4D Agent is ready to process dataset URLs")
    print("Sample usage (requires ANTHROPIC_API_KEY):")
    print("  python test_d4d.py")
    
    print(f"\n3. Supported URL types:")
    print("  - PDF documents (auto-detected by .pdf extension or Content-Type)")
    print("  - Web pages (HTML content extracted and cleaned)")
    print("  - Dataset documentation pages")
    
    print(f"\n4. Output format:")
    print("  - YAML document conforming to D4D schema")
    print("  - Includes dataset composition, collection, preprocessing, etc.")
    
    print(f"\n5. Example dataset URLs that could be processed:")
    example_urls = [
        "https://archive.ics.uci.edu/ml/datasets/iris",
        "https://www.kaggle.com/datasets/uciml/iris",
        "https://physionet.org/content/mimic-cxr/2.0.0/",
    ]
    for url in example_urls:
        print(f"  - {url}")
        
    print(f"\nTo use the D4D agent:")
    print(f"1. Set your API key: export ANTHROPIC_API_KEY='your-key-here'")
    print(f"2. Run: python test_d4d.py")


if __name__ == "__main__":
    asyncio.run(demo_d4d_functionality())