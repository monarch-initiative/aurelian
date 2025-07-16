"""
Gradio Interface for Knowledge Agent.
"""
import asyncio
import tempfile
from pathlib import Path
from typing import Tuple, Optional

import gradio as gr

from .knowledge_agent_agent import run_sync
from .knowledge_agent_config import get_config


def extract_entities_sync(text: str, schema: str = None, generate_schema: bool = False) -> Tuple[str, str]:
    """
    Extract entities from text with optional schema generation.
    
    Returns:
        Tuple of (status_message, extracted_json)
    """
    if not text.strip():
        return "❌ Please provide text to extract from", ""
    
    try:
        if generate_schema and not schema.strip():
            # Generate schema automatically
            prompt = f"""
            Generate a schema for entity extraction, then extract entities from this text:
            
            {text}
            """
        elif schema.strip():
            # Use provided schema
            prompt = f"""
            Schema:
            {schema}
            
            Text:
            {text}
            
            Extract entities according to the schema.
            """
        else:
            # Simple extraction without schema
            prompt = f"""
            Extract entities from this text:
            {text}
            """
        
        result = run_sync(prompt)
        return "✅ Extraction completed!", str(result.output)
        
    except Exception as e:
        return f"❌ Extraction error: {str(e)}", ""


def generate_schema_sync(description: str) -> Tuple[str, str]:
    """
    Generate a LinkML schema from description.
    
    Returns:
        Tuple of (status_message, schema_yaml)
    """
    if not description.strip():
        return "❌ Please provide a schema description", ""
    
    try:
        prompt = f"Generate a LinkML schema for: {description}"
        result = run_sync(prompt)
        
        return "✅ Schema generated successfully!", str(result.output)
        
    except Exception as e:
        return f"❌ Schema generation error: {str(e)}", ""


def load_example_text(domain: str) -> str:
    """Load example text based on domain selection."""
    examples = {
        "Biomedical": """BRCA1 mutations are associated with hereditary breast and ovarian cancer syndrome.
The p.Gly1788Val variant in BRCA1 has been linked to increased cancer risk.
Patients typically present with early-onset breast cancer and family history.""",
        
        "Chemistry": """The Suzuki coupling of 4-bromobenzaldehyde with phenylboronic acid 
using Pd(PPh3)4 catalyst in DMF at 80°C yielded biphenyl-4-carbaldehyde 
in 92% yield after 6 hours.""",
        
        "Business": """Apple Inc. reported Q3 2024 revenue of $85.8 billion, up 5% year-over-year.
iPhone sales contributed $46.2 billion to total revenue.
The company's services segment grew 14% to $24.2 billion.""",
        
        "Clinical": """Patient presents with hypertrophic cardiomyopathy caused by MYH7 mutation.
Family history reveals MYBPC3 variants associated with cardiac dysfunction.
Echocardiogram shows left ventricular outflow obstruction."""
    }
    return examples.get(domain, "")


def chat(deps=None, **kwargs):
    """Create the Gradio interface for Knowledge Agent."""
    
    with gr.Blocks(title="Knowledge Agent", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 🧠 Knowledge Agent
        
        Extract structured knowledge from scientific text with automatic schema generation and validation.
        
        **Features:**
        - 🤖 AI-powered entity extraction
        - 📋 Automatic schema generation
        - 🎯 Ontology grounding with curator info
        - ✅ Real-time validation
        """)
        
        with gr.Tabs():
            # Tab 1: Entity Extraction
            with gr.Tab("Extract Entities"):
                gr.Markdown("### 📝 Extract structured entities from text")
                
                with gr.Row():
                    with gr.Column(scale=3):
                        text_input = gr.Textbox(
                            label="Input Text",
                            placeholder="Enter text for entity extraction...",
                            lines=8
                        )
                    with gr.Column(scale=1):
                        domain_dropdown = gr.Dropdown(
                            choices=["Biomedical", "Chemistry", "Business", "Clinical"],
                            label="Example Domains",
                            value=None
                        )
                
                with gr.Row():
                    schema_input = gr.Code(
                        label="LinkML Schema (Optional)",
                        language="yaml",
                        lines=10
                    )
                
                with gr.Row():
                    generate_schema_checkbox = gr.Checkbox(
                        label="Auto-generate schema if not provided",
                        value=True
                    )
                    extract_btn = gr.Button("🔍 Extract Entities", variant="primary")
                
                status_output = gr.Textbox(label="Status", interactive=False)
                results_output = gr.Code(label="Extracted Entities (JSON)", language="json", lines=15)
            
            # Tab 2: Schema Generation
            with gr.Tab("Generate Schema"):
                gr.Markdown("### 🔧 Generate LinkML schemas for entity extraction")
                
                schema_description = gr.Textbox(
                    label="Schema Description",
                    placeholder="e.g., genes, diseases, and their relationships from biomedical text",
                    lines=3
                )
                
                generate_schema_btn = gr.Button("🔧 Generate Schema", variant="primary")
                
                schema_status = gr.Textbox(label="Status", interactive=False)
                generated_schema = gr.Code(label="Generated Schema", language="yaml", lines=20)
                
                # Copy schema to extraction tab
                copy_schema_btn = gr.Button("📋 Use This Schema for Extraction")
            
            # Tab 3: Combined Workflow
            with gr.Tab("Complete Workflow"):
                gr.Markdown("### 🚀 End-to-end extraction: Schema generation + Entity extraction")
                
                workflow_description = gr.Textbox(
                    label="What to Extract",
                    placeholder="e.g., extract genes, diseases, and treatments from clinical text",
                    lines=2
                )
                
                workflow_text = gr.Textbox(
                    label="Input Text",
                    placeholder="Enter text for extraction...",
                    lines=10
                )
                
                workflow_btn = gr.Button("🚀 Generate Schema & Extract", variant="primary")
                
                workflow_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Row():
                    workflow_schema = gr.Code(label="Generated Schema", language="yaml", scale=1)
                    workflow_results = gr.Code(label="Extraction Results", language="json", scale=1)
            
            # Tab 4: Help & Examples
            with gr.Tab("Help & Examples"):
                gr.Markdown("""
                ### 📚 How to Use the Knowledge Agent
                
                **1. Entity Extraction:**
                - Paste your text in the input field
                - Optionally provide a LinkML schema
                - If no schema provided, one will be auto-generated
                - Click "Extract Entities" to get structured results
                
                **2. Schema Generation:**
                - Describe what you want to extract
                - Click "Generate Schema" to create a LinkML schema
                - Copy the schema to use in extraction
                
                **3. Complete Workflow:**
                - Describe extraction goals and provide text
                - Get both schema and extraction results in one step
                
                ### 🔧 Example Descriptions
                
                **Biomedical:**
                - "genes, diseases, and phenotypes from clinical text"
                - "drug names, dosages, and side effects"
                - "protein-protein interactions with confidence scores"
                
                **Chemistry:**
                - "chemical reactions with yields and conditions"
                - "compounds, catalysts, and reaction temperatures"
                
                **Business:**
                - "companies, products, and financial metrics"
                - "market segments and performance indicators"
                
                ### 🎯 Output Features
                
                The Knowledge Agent provides:
                - **Ontology Grounding**: Entities mapped to standard ontologies
                - **Confidence Scores**: Extraction and grounding confidence
                - **Curator Information**: Match types (label vs synonym) and notes
                - **Structured JSON**: Ready for downstream analysis
                """)
        
        # Event handlers
        domain_dropdown.change(
            fn=load_example_text,
            inputs=[domain_dropdown],
            outputs=[text_input]
        )
        
        extract_btn.click(
            fn=extract_entities_sync,
            inputs=[text_input, schema_input, generate_schema_checkbox],
            outputs=[status_output, results_output]
        )
        
        generate_schema_btn.click(
            fn=generate_schema_sync,
            inputs=[schema_description],
            outputs=[schema_status, generated_schema]
        )
        
        copy_schema_btn.click(
            fn=lambda x: x,
            inputs=[generated_schema],
            outputs=[schema_input]
        )
        
        def complete_workflow(description, text):
            # Generate schema and extract in one step
            if not description.strip() or not text.strip():
                return "❌ Please provide both description and text", "", ""
            
            try:
                prompt = f"""
                Generate a schema for: {description}
                
                Then extract entities from this text:
                {text}
                
                Return both the schema and extraction results.
                """
                
                result = run_sync(prompt)
                # For simplicity, return result in both outputs
                # In practice, you'd parse the result to separate schema and entities
                return "✅ Workflow completed!", str(result.output), str(result.output)
                
            except Exception as e:
                return f"❌ Workflow error: {str(e)}", "", ""
        
        workflow_btn.click(
            fn=complete_workflow,
            inputs=[workflow_description, workflow_text],
            outputs=[workflow_status, workflow_schema, workflow_results]
        )
    
    return interface


def launch_gradio(share: bool = False, server_port: int = 7860):
    """Launch the Gradio interface."""
    interface = chat()
    interface.launch(share=share, server_port=server_port)


if __name__ == "__main__":
    launch_gradio()