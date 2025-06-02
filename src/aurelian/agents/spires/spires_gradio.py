"""
Gradio interface for the SPIRES agent.
"""
import os
from pathlib import Path
import gradio as gr
import logfire

from aurelian.agents.spires.spires_agent import spires_agent
from aurelian.agents.spires.spires_config import SPIRESDependencies, get_config

DEFAULT_TEMPLATES = [
    "biological_process.BiologicalProcess",
    "gocam.GoCamAnnotations", 
    "drug.DrugMechanism",
    "human_phenotype.HumanPhenotype"
]


def chat(deps: SPIRESDependencies = None, model=None, **kwargs):
    """
    Create a Gradio interface for the SPIRES agent.
    
    Args:
        deps: The agent dependencies
        model: Optional model override
        **kwargs: Additional parameters to pass to the agent
        
    Returns:
        A Gradio interface
    """
    with logfire.span("chat"):
        # Initialize dependencies
        if deps is None:
            deps = get_config()
            
        # Set environment variables if not already set
        if not os.environ.get("SPIRES_TEMPLATE"):
            os.environ["SPIRES_TEMPLATE"] = DEFAULT_TEMPLATES[0]
            
        # Initialize the active template
        if not hasattr(deps, "template_name") or not deps.template_name:
            deps.template_name = os.environ.get("SPIRES_TEMPLATE", DEFAULT_TEMPLATES[0])
            
        # Pass model if provided
        if model:
            deps.model = model
            
        # Set up file upload directory
        uploads_dir = Path(deps.workdir.location) / "uploads"
        uploads_dir.mkdir(exist_ok=True, parents=True)
            
        # Create the Gradio interface
        with gr.Blocks(title="SPIRES - Structured Knowledge Extraction") as demo:
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("# SPIRES Agent")
                    gr.Markdown("""
                    ## Structured Knowledge Extraction from Scientific Text
                    
                    This agent extracts structured knowledge from scientific text using OntoGPT templates.
                    - **Select a template** appropriate for your knowledge domain
                    - **Submit text** directly or upload a file
                    - **Extract knowledge** in a structured format with ontology grounding
                    
                    The extracted knowledge will be linked to standard ontologies like Gene Ontology, 
                    MONDO Disease Ontology, ChEBI, and more.
                    """)
                    
            with gr.Row():
                with gr.Column(scale=2):
                    # Template selector
                    template_dropdown = gr.Dropdown(
                        choices=DEFAULT_TEMPLATES,
                        value=deps.template_name,
                        label="Knowledge Extraction Template",
                        info="Select the template appropriate for your text content",
                    )
                    
                    # Grounding toggle
                    grounding_checkbox = gr.Checkbox(
                        value=deps.enable_grounding,
                        label="Enable Entity Grounding",
                        info="Link extracted entities to ontologies (may increase processing time)"
                    )
                    
                    # Input methods
                    with gr.Tab("Text Input"):
                        text_input = gr.Textbox(
                            lines=10,
                            placeholder="Enter scientific text to extract knowledge from...",
                            label="Input Text"
                        )
                        
                    with gr.Tab("File Upload"):
                        file_input = gr.File(
                            label="Upload PDF, TXT, or other document",
                            file_types=["pdf", "txt", "md", "html"]
                        )
                        
                    with gr.Tab("PaperQA Query"):
                        query_input = gr.Textbox(
                            lines=3,
                            placeholder="Query PaperQA collection (e.g., 'What is known about Alzheimer's disease mechanisms?')",
                            label="PaperQA Query"
                        )
                    
                    # Submit buttons
                    with gr.Row():
                        text_button = gr.Button("Extract from Text", variant="primary")
                        file_button = gr.Button("Extract from File")
                        query_button = gr.Button("Query & Extract")
                        
                with gr.Column(scale=3):
                    # Output display
                    output_display = gr.JSON(label="Extracted Knowledge")
                    
                    with gr.Accordion("How to read the results", open=False):
                        gr.Markdown("""
                        ### Understanding the output format
                        
                        The extraction results include:
                        - **template_used**: The template used for extraction
                        - **extracted_data**: The main structured knowledge
                        - **grounded_entities**: Ontology mappings for extracted terms
                        - **metadata**: Processing information
                        
                        Each template has a different schema. For example:
                        - Biological Process template extracts processes, participants, and locations
                        - Drug Mechanism template extracts drugs, targets, and mechanisms
                        - Human Phenotype template extracts diseases, phenotypes, and genetics
                        
                        Terms marked with ontology IDs (e.g., "MONDO:0005148") are grounded to standard ontologies.
                        """)
            
            # Example prompts
            with gr.Accordion("Example inputs", open=False):
                gr.Examples(
                    [
                        ["The MAPK signaling pathway plays a crucial role in cell proliferation and differentiation. ERK1/2 are activated by upstream kinases MEK1/2, which are phosphorylated by RAF proteins. Upon activation, ERK1/2 translocate to the nucleus where they phosphorylate transcription factors like ELK1 and c-Myc, leading to gene expression changes."],
                        ["Amyloid beta (Aβ) peptides are known to aggregate and form plaques in the brains of patients with Alzheimer's disease. These plaques disrupt neuronal function and trigger inflammatory responses, eventually leading to neurodegeneration and cognitive decline."],
                        ["PARP inhibitors like Olaparib work by blocking the action of poly(ADP-ribose) polymerase (PARP) enzymes, which help repair DNA damage in cancer cells. In tumors with BRCA mutations, which already have DNA repair defects, PARP inhibition leads to synthetic lethality and cell death."]
                    ],
                    inputs=[text_input],
                    label="Example scientific texts"
                )
                
                gr.Examples(
                    [
                        ["What are the key mechanisms of PARP inhibitors in cancer treatment?"],
                        ["How does amyloid beta contribute to Alzheimer's disease pathology?"],
                        ["What is the role of autophagy in neurodegenerative diseases?"]
                    ],
                    inputs=[query_input],
                    label="Example PaperQA queries"
                )
            
            # Event handlers
            def update_template(template):
                """Update the agent's template."""
                deps.template_name = template
                os.environ["SPIRES_TEMPLATE"] = template
                return f"Template changed to: {template}"
            
            def update_grounding(enable):
                """Update the agent's grounding setting."""
                deps.enable_grounding = enable
                os.environ["SPIRES_ENABLE_GROUNDING"] = str(enable).lower()
                return None
                
            async def extract_from_text(text):
                """Extract knowledge from text."""
                if not text or len(text.strip()) < 10:
                    return {"error": "Text input is too short or empty."}
                    
                result = await spires_agent.run(text, deps=deps)
                return result.data
                
            async def extract_from_file_upload(file):
                """Extract knowledge from uploaded file."""
                if not file:
                    return {"error": "No file uploaded."}
                    
                # Prepare file path to pass to agent
                file_path = file.name
                result = await spires_agent.run(f"Extract knowledge from file: {file_path}", deps=deps)
                return result.data
                
            async def extract_from_query(query):
                """Query PaperQA and extract knowledge."""
                if not query or len(query.strip()) < 5:
                    return {"error": "Query is too short or empty."}
                    
                result = await spires_agent.run(f"Search PaperQA for: {query}", deps=deps)
                return result.data
            
            # Connect event handlers
            template_dropdown.change(update_template, inputs=template_dropdown, outputs=gr.Textbox(visible=False))
            grounding_checkbox.change(update_grounding, inputs=grounding_checkbox, outputs=gr.Textbox(visible=False))
            
            text_button.click(extract_from_text, inputs=text_input, outputs=output_display)
            file_button.click(extract_from_file_upload, inputs=file_input, outputs=output_display)
            query_button.click(extract_from_query, inputs=query_input, outputs=output_display)
            
        return demo


if __name__ == "__main__":
    # Simple test to verify the module loads correctly
    ui = chat()
    ui.launch()