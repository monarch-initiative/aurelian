# Aurelian Development Guide

## Build & Test Commands
- Run all tests: `uv run pytest`
- Run single test: `uv run pytest tests/test_agents/test_linkml_agent.py::test_specific_function`
- Run specific test module: `uv run pytest tests/test_agents/test_linkml_agent.py`
- Lint code: `uv run ruff check src/ tests/`
- Fix lint issues: `uv run ruff check --fix src/ tests/`
- Format code: `uv run black src/ tests/`
- Type check: `uv run mypy src tests`
- Build docs: `uv run mkdocs build`
- Serve docs: `make serve` or `uv run mkdocs serve`
- Generate test reports: `make reports/all.md`

## Code Style Guidelines
- Use Black formatting (line-length=120)
- Follow PEP 8 with Ruff linting
- Type annotations required for function signatures
- Class attributes should have type annotations
- Use snake_case for functions/variables, PascalCase for classes
- Import order: stdlib, third-party, local
- Error handling: use appropriate exceptions with meaningful messages
- Docstrings required for all public functions/methods/classes
- Tests located in tests/ directory matching module structure

## Creating New Agents

Each agent in Aurelian follows a consistent structure with these key components:

1. **Main Agent Module** (`agent_name_agent.py`):
   - Contains the core agent implementation
   - Defines the agent's capabilities and behavior
   - Registers the agent with the system

2. **Configuration Module** (`agent_name_config.py`):
   - Defines dependencies and configuration settings
   - Uses Pydantic models for configuration validation
   - Handles environment-specific settings

3. **Gradio Interface** (`agent_name_gradio.py`):
   - Creates a web UI for the agent
   - Defines example prompts for testing
   - Manages interaction between user and agent

4. **Tools Module** (`agent_name_tools.py`):
   - Implements agent-specific utility functions
   - Provides domain-specific capabilities
   - Interfaces with external resources

5. **Evaluation Module** (`agent_name_evals.py`):
   - Defines test cases for agent evaluation
   - Implements evaluation metrics
   - Uses pydantic-evals framework

### Steps to Create a New Agent

1. Create a new directory under `src/aurelian/agents/`
2. Implement the required modules following the template structure
3. Register the agent in the CLI (update `src/aurelian/cli.py`)
4. Add documentation in the `docs/agents/` directory
5. Create tests in the `tests/test_agents/` directory

## Adding Evaluations

Aurelian uses the pydantic-evals framework for systematic agent evaluation. Each agent should have an evaluation module (`agent_name_evals.py`) with these components:

### Evaluation Module Structure

```python
# Import necessary components
from aurelian.evaluators.model import MetadataDict, metadata
from aurelian.evaluators.substring_evaluator import SubstringEvaluator
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import LLMJudge

# Define metadata class
class AgentNameMetadata(Dict[str, Any]):
    """Simple metadata dictionary for Agent evaluations."""
    pass

# Define individual test cases
case1 = Case(
    name="test_name",
    inputs="Test question or prompt",
    expected_output="expected substring",  # Used by SubstringEvaluator
    metadata=metadata("difficulty_level", "category")
)

# Add case-specific evaluator (optional)
case2 = Case(
    name="complex_test",
    inputs="Complex question",
    expected_output="expected substring",
    metadata=metadata("hard", "complex_category"),
    evaluators=[
        LLMJudge(
            rubric="Detailed evaluation criteria",
            include_input=True
        )
    ]
)

# Create the evaluation dataset
def create_eval_dataset() -> Dataset[str, str, MetadataDict]:
    """Create a dataset for evaluating the agent."""
    
    # Collect all cases
    cases = [case1, case2, ...]
    
    # Dataset-level evaluators
    evaluators = [
        SubstringEvaluator(),
        LLMJudge(
            rubric="General evaluation criteria",
            model="anthropic:claude-3-7-sonnet-latest"
        )
    ]
    
    return Dataset(
        cases=cases,
        evaluators=evaluators
    )
```

### Best Practices for Evaluations

1. **Test Case Design**:
   - Base test cases on the agent's Gradio examples
   - Include a range of difficulty levels (easy, medium, hard)
   - Cover all core functionalities of the agent
   - Provide descriptive names and categories

2. **Evaluation Criteria**:
   - Use both simple substring matching and semantic evaluation
   - Include domain-specific evaluation criteria
   - Create comprehensive rubrics for LLMJudge
   - Consider both accuracy and quality in evaluations

3. **Metadata Usage**:
   - Tag test cases with meaningful metadata
   - Use consistent difficulty levels across agents
   - Categorize tests by functionality
   - Add domain-specific metadata as needed

4. **Running Evaluations**:
   - Use the standard evaluation runner
   - Track evaluation results over time
   - Use evaluations to guide agent improvements