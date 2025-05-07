# PaperQA Agent

The PaperQA Agent provides powerful scientific literature search and analysis capabilities within Aurelian. It integrates PaperQA's retrieval-augmented generation abilities to find relevant papers, analyze their contents, and generate comprehensive answers based on scientific literature.

## Features

- Search for scientific papers on specific topics
- Query papers to answer research questions
- Add papers by file path or URL
- Generate comprehensive reports based on literature
- List all papers in the current collection

## Usage

### Python API

```python
from aurelian.agents.paperqa import paperqa_agent, get_config

# Initialize dependencies with your paper directory
deps = get_config()
deps.paper_directory = "/path/to/papers"

# Customize settings (all settings are optional)
deps.llm = "claude-3-sonnet-20240229"  # Use Claude instead of default GPT-4
deps.temperature = 0.5  # Increase temperature for more creative responses
deps.evidence_k = 15  # Retrieve more evidence pieces for better context
deps.chunk_size = 3000  # Use smaller chunks for more granular retrieval

# Search for papers on a topic
search_result = await paperqa_agent.run(
    "Search for papers on CRISPR gene editing",
    deps=deps
)

# Ask a question about the papers
query_result = await paperqa_agent.run(
    "What are the main challenges in CRISPR gene editing?",
    deps=deps
)

# Print the results
print(search_result.data.session.answer)
print(query_result.data.session.formatted_answer)  # Includes citations
```

### CLI
```
# Search for papers
aurelian paperqa --paper-directory "/path/to/papers" "Search for papers on CRISPR gene editing"

# Ask a question with customized settings
aurelian paperqa --paper-directory "/path/to/papers" --embedding "text-embedding-3-large" --temperature 0.2 "What are the main challenges in CRISPR gene editing?"

# Start the chat interface
aurelian paperqa --paper-directory "/path/to/papers" --ui
```

### Webinterface
```
aurelian paperqa --paper-directory "/path/to/papers" --ui
```