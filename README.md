[![DOI](https://zenodo.org/badge/932483388.svg)](https://doi.org/10.5281/zenodo.15299996)

# Aurelian: Agentic Universal Research Engine for Literature, Integration, Annotation, and Navigation

| [Documentation](https://monarch-initiative.github.io/aurelian) |

```
aurelian --help
```

Most commands will start up a different AI agent.

## Examples of use

### D4D Agent (Datasheets for Datasets)

Extracts structured metadata from dataset documentation following the [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) framework.

**Supported File Types**: PDF, HTML, JSON, text/markdown (both URLs and local files)

**Library Usage**:
```python
from aurelian.agents.d4d.d4d_agent import d4d_agent
from aurelian.agents.d4d.d4d_config import D4DConfig

# Process multiple sources
sources = [
    "https://example.com/dataset",
    "/path/to/metadata.json",
    "/path/to/documentation.html"
]

config = D4DConfig()
result = await d4d_agent.run(
    f"Extract metadata from: {', '.join(sources)}",
    deps=config
)

print(result.data)  # D4D YAML output
```

**Test Script**:
```bash
cd aurelian
python test_d4d.py
```

**Features**:
- Automatic file type detection (PDF, HTML, JSON, text)
- Both URLs and local file paths supported
- Content truncation at 50,000 characters for token management
- Structured YAML output following D4D schema

**Documentation**: [D4D Agent Guide](docs/agents/d4d_agent/)

---

### TALISMAN

gene set enrichment

### Aria

checking papers against checklists

### GO-CAM agent

This agent is for exploring, chatting with, and reviewing GO-CAMs

Docs: [gocam_agent](https://monarch-initiative.github.io/aurelian/agents/gocam_agent/)

It can be used to generate reviews according to guidelines for GO-CAMs:

* [GO-CAM Reviews](https://cmungall.github.io/go-cam-reviews/)

It can also generate SVGs, demonstrating innate knowledge of both the visual grammar of pathway diagrams and the semantics of the underlying biology.


<img alt="img" src="https://cmungall.github.io/go-cam-reviews/figures/FIG-646ff70100005137-IL33_signaling_pathway__Human_.svg" />

### GO-Ann agent

This agent is for exploring, chatting with, and reviewing standard annotations


Docs: [go_ann_agent](https://monarch-initiative.github.io/aurelian/agents/go_ann_agent/)

Example review using TF guidelines:

https://github.com/geneontology/go-annotation/issues/5743

## Troubleshooting

### Installing linkml-store

Some agents require linkml-store pre-indexed. E.g. a mongodb with gocams for cam agent.
Consult the [linkml-store documentation](https://linkml.io/linkml-store/) for more information.

### Semantic search over ontologies

If an agent requires ontology search it will use the semsql/OAK sqlite database.
The first time querying it will use linkml-store to create an LLM index. Requires OAI key.
This may be slow first iteration. Will be cached until your pystow cache regenerates.
