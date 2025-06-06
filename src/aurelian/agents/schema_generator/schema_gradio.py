"""
Gradio Interface for Schema Generator Agent.
"""
import asyncio
import tempfile
from pathlib import Path
from typing import Tuple, Optional

import gradio as gr
import yaml

from .schema_agent import run_with_validation
from .schema_generator_config import get_config


async def generate_schema_async(description: str, model: str) -> Tuple[str, str]:
    """
    Generate and validate a schema asynchronously.
    
    Returns:
        Tuple of (status_message, schema_yaml)
    """
    if not description.strip():
        return "Please provide a description", ""
    
    try:
        deps = get_config()
        
        # Generate and validate schema
        schema_yaml = await run_with_validation(description, deps)
        
        if "validation failed" in schema_yaml.lower() or "error" in schema_yaml.lower():
            return f"{schema_yaml}", ""
        
        return "Schema generated and validated successfully!", schema_yaml
        
    except Exception as e:
        return f"Error: {str(e)}", ""


def generate_schema_sync(description: str, model: str) -> Tuple[str, str]:
    """Synchronous wrapper for Gradio."""
    return asyncio.run(generate_schema_async(description, model))


async def validate_schema_async(schema_yaml: str) -> str:
    """
    Validate a schema asynchronously.
    
    Returns:
        Validation status message
    """
    if not schema_yaml.strip():
        return "Please provide a schema to validate"
    
    try:
        # Use LinkML validation directly
        from aurelian.agents.linkml.linkml_tools import validate_then_save_schema
        from aurelian.agents.linkml.linkml_config import get_config as get_linkml_config
        
        class MockContext:
            def __init__(self, deps):
                self.deps = deps
        
        linkml_deps = get_linkml_config()
        ctx = MockContext(linkml_deps)
        
        result = await validate_then_save_schema(ctx, schema_yaml, None)
        
        if result.valid:
            messages = "\n".join(result.info_messages or [])
            return f"Schema is valid!\n{messages}"
        else:
            return "Schema validation failed"
            
    except Exception as e:
        return f"Validation error: {str(e)}"


def validate_schema_sync(schema_yaml: str) -> str:
    """Synchronous wrapper for Gradio."""
    return asyncio.run(validate_schema_async(schema_yaml))


async def extract_entities_async(text: str, schema_yaml: str) -> Tuple[str, str]:
    """
    Extract entities from text using schema.
    
    Returns:
        Tuple of (status_message, extracted_json)
    """
    if not text.strip():
        return "Please provide text to extract from", ""
    
    if not schema_yaml.strip():
        return "Please provide a schema", ""
    
    try:
        # Use knowledge agent for extraction
        from aurelian.agents.knowledge_agent.knowledge_agent_agent import run_sync
        
        prompt = f"""
        Schema:
        {schema_yaml}
        
        Text:
        {text}
        
        Extract entities according to the schema and return structured JSON.
        """
        
        result = run_sync(prompt)
        
        return "Extraction completed!", str(result.output)
        
    except Exception as e:
        return f"Extraction error: {str(e)}", ""


def extract_entities_sync(text: str, schema_yaml: str) -> Tuple[str, str]:
    """Synchronous wrapper for Gradio."""
    return asyncio.run(extract_entities_async(text, schema_yaml))


def load_example_schema(domain: str) -> str:
    """Load example schema based on domain selection."""
    examples = {
        "Biomedical": "genes, diseases, and phenotypes from clinical text",
        "Chemistry": "chemical reactions with yields and conditions", 
        "Real Estate": "houses, prices, and neighborhood features",
        "Business": "companies, products, and market segments",
        "Academic": "research topics, methodologies, and findings"
    }
    return examples.get(domain, "")


def save_schema_file(schema_yaml: str, filename: str) -> str:
    """Save schema to a file."""
    if not schema_yaml.strip():
        return "No schema to save"
    
    if not filename.strip():
        filename = "generated_schema.yaml"
    
    if not filename.endswith('.yaml'):
        filename += '.yaml'
    
    try:
        # Save to temporary directory for download
        temp_dir = Path(tempfile.gettempdir())
        file_path = temp_dir / filename
        file_path.write_text(schema_yaml)
        return f"Schema saved to: {file_path}"
    except Exception as e:
        return f"Save error: {str(e)}"


def create_gradio_interface():
    """Create the Gradio interface for Schema Generator."""
    
    with gr.Blocks(title="Schema Generator", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        #Schema Generator Agent
        
        Create and validate sophisticated LinkML schemas for entity extraction from any domain.
        """)
        
        with gr.Tabs():
            # Tab 1: Schema Generation
            with gr.Tab("Generate Schema"):
                gr.Markdown("### Describe what you want to extract")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        description_input = gr.Textbox(
                            label="Schema Description",
                            placeholder="e.g., genes, diseases, and phenotypes from clinical text",
                            lines=3
                        )
                    with gr.Column(scale=1):
                        domain_dropdown = gr.Dropdown(
                            choices=["Biomedical", "Chemistry", "Real Estate", "Business", "Academic"],
                            label="Example Domains",
                            value=None
                        )
                
                with gr.Row():
                    model_dropdown = gr.Dropdown(
                        choices=["openai:gpt-4o", "openai:gpt-4", "anthropic:claude-3-sonnet"],
                        value="openai:gpt-4o",
                        label="Model"
                    )
                    generate_btn = gr.Button("Generate Schema", variant="primary")
                
                status_output = gr.Textbox(label="Status", interactive=False)
                schema_output = gr.Code(label="Generated Schema", language="yaml", lines=20)
                
                with gr.Row():
                    filename_input = gr.Textbox(
                        label="Filename",
                        value="generated_schema.yaml",
                        scale=3
                    )
                    save_btn = gr.Button("Save Schema", scale=1)
                
                save_status = gr.Textbox(label="Save Status", interactive=False)
            
            # Tab 2: Schema Validation
            with gr.Tab("Validate Schema"):
                gr.Markdown("### Validate existing LinkML schemas")
                
                schema_input = gr.Code(
                    label="LinkML Schema (YAML)",
                    language="yaml",
                    lines=15
                )
                
                validate_btn = gr.Button("Validate Schema", variant="primary")
                validation_output = gr.Textbox(label="Validation Result", lines=5)
            
            # Tab 3: Entity Extraction
            with gr.Tab("Test Extraction"):
                gr.Markdown("### 🔍 Test entity extraction with your schema")
                
                with gr.Row():
                    with gr.Column():
                        text_input = gr.Textbox(
                            label="Text to Extract From",
                            placeholder="Enter text for entity extraction...",
                            lines=8
                        )
                    with gr.Column():
                        test_schema_input = gr.Code(
                            label="Schema (YAML)",
                            language="yaml",
                            lines=8
                        )
                
                extract_btn = gr.Button("🔍 Extract Entities", variant="primary")
                
                with gr.Row():
                    extraction_status = gr.Textbox(label="Status", scale=1)
                    extracted_output = gr.Code(label="Extracted Entities (JSON)", language="json", scale=2)
            
            # Tab 4: Examples & Help
            with gr.Tab("Examples & Help"):
                gr.Markdown("""
                ### 📚 Example Schema Descriptions
                
                **Biomedical:**
                - genes, diseases, and phenotypes from clinical text
                - drug names, dosages, and side effects from medical literature
                - protein-protein interactions with confidence scores
                
                **Chemistry:**
                - chemical reactions with yields and conditions
                - catalysts, solvents, and reaction temperatures
                - molecular structures and properties
                
                ### 🛠How to Use
                
                1. **Generate**: Describe what you want to extract
                2. **Validate**: Check if your schema is valid LinkML
                3. **Test**: Try extraction on sample text
                4. **Save**: Download your schema for later use
                
                ### 🔗 Integration
                
                Generated schemas can be used with:
                - Knowledge Agent for text extraction
                - LinkML tools for data validation
                - Any OntoGPT-compatible system
                """)
        
        domain_dropdown.change(
            fn=load_example_schema,
            inputs=[domain_dropdown],
            outputs=[description_input]
        )
        
        generate_btn.click(
            fn=generate_schema_sync,
            inputs=[description_input, model_dropdown],
            outputs=[status_output, schema_output]
        )
        
        save_btn.click(
            fn=save_schema_file,
            inputs=[schema_output, filename_input],
            outputs=[save_status]
        )
        
        validate_btn.click(
            fn=validate_schema_sync,
            inputs=[schema_input],
            outputs=[validation_output]
        )
        
        extract_btn.click(
            fn=extract_entities_sync,
            inputs=[text_input, test_schema_input],
            outputs=[extraction_status, extracted_output]
        )
    
    return interface


def launch_gradio(share: bool = False, server_port: int = 7860):
    """Launch the Gradio interface."""
    interface = create_gradio_interface()
    interface.launch(share=share, server_port=server_port)


if __name__ == "__main__":
    launch_gradio()