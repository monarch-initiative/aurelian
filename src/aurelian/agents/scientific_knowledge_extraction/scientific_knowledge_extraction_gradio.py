"""Gradio interface for the Scientific Knowledge Extraction Agent."""

import os
import json
import asyncio
import tempfile
import gradio as gr
import pandas as pd
from typing import Dict, List, Optional, Tuple

# Importing only the agent, will use dict for messages
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_agent import scientific_knowledge_extraction_agent
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools import (
    map_to_biolink,
    ground_to_ontology,
    export_to_kgx,
    read_pdf,
    extract_knowledge,
    create_kg_edges
)

# Global state for the Gradio app
class AppState:
    def __init__(self):
        self.pdf_directory = None
        self.cache_directory = None
        self.dependencies = None
        self.history = []
        self.current_pdfs = []
        self.extracted_knowledge = []

state = AppState()

async def chat_with_agent(message: str, history: List[List[str]]) -> List[List[str]]:
    """Process a message with the agent and update the chat history."""
    if not state.dependencies:
        return [], "Please set up the PDF directory first."
    
    # Add user message to history
    state.history.append(["User", message])
    
    # Process with agent
    try:
        response = await scientific_knowledge_extraction_agent.chat(
            messages=[{"role": "user", "content": message}],
            dependencies=state.dependencies
        )
        
        # Add agent response to history
        state.history.append(["Agent", response.content])
        
        # Convert history to Gradio messages format
        gradio_history = []
        for i in range(0, len(state.history), 2):
            if i+1 < len(state.history):
                user_msg = state.history[i][1]
                agent_msg = state.history[i+1][1]
                gradio_history.append({"role": "user", "content": user_msg})
                gradio_history.append({"role": "assistant", "content": agent_msg})
        
        return gradio_history, ""
    except Exception as e:
        # Format the error as messages
        error_msg = f"Error: {str(e)}"
        return [{"role": "user", "content": message}, {"role": "assistant", "content": error_msg}], error_msg


def setup_directories(pdf_dir: str, cache_dir: Optional[str] = None) -> str:
    """Set up the PDF and cache directories."""
    try:
        # Validate PDF directory
        if not os.path.exists(pdf_dir):
            return f"Error: PDF directory '{pdf_dir}' does not exist."
        
        # Use specified cache directory or create a default one
        final_cache_dir = cache_dir if cache_dir else os.path.join(pdf_dir, ".scientific_knowledge_cache")
        
        # Create dependencies
        state.pdf_directory = pdf_dir
        state.cache_directory = final_cache_dir
        state.dependencies = ScientificKnowledgeExtractionDependencies(
            pdf_directory=pdf_dir,
            cache_directory=final_cache_dir
        )
        
        # Get initial list of PDFs
        pdf_files = []
        for filename in os.listdir(pdf_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(pdf_dir, filename)
                is_processed = state.dependencies.is_processed(file_path)
                pdf_files.append({
                    "file_path": file_path,
                    "filename": filename,
                    "is_processed": is_processed
                })
        
        state.current_pdfs = pdf_files
        
        return f"Successfully set up directories. Found {len(pdf_files)} PDF files."
    except Exception as e:
        return f"Error setting up directories: {str(e)}"


def get_pdf_list() -> pd.DataFrame:
    """Get the list of PDFs as a DataFrame for display."""
    if not state.current_pdfs:
        return pd.DataFrame(columns=["Filename", "Processed"])
    
    return pd.DataFrame([
        {"Filename": pdf["filename"], "Processed": "Yes" if pdf["is_processed"] else "No"}
        for pdf in state.current_pdfs
    ])


async def process_all_pdfs() -> str:
    """Process all unprocessed PDFs in the directory."""
    if not state.dependencies:
        return "Please set up the PDF directory first."
    
    try:
        # Create a RunContext for the tools
        class RunContext:
            def __init__(self, deps):
                self.dependencies = deps
                
        ctx = RunContext(state.dependencies)
        
        # Process each PDF file
        processed_count = 0
        total_edges = 0
        
        # Get the list of PDF files
        for pdf_file in state.current_pdfs:
            if not pdf_file.get("is_processed", False):
                file_path = pdf_file["file_path"]
                try:
                    # Read the PDF
                    pdf_data = await read_pdf(ctx, file_path)
                    
                    # Extract knowledge
                    edges = await extract_knowledge(ctx, pdf_data)
                    
                    # Process edges if any were found
                    if edges:
                        processed_count += 1
                        total_edges += len(edges)
                        # Mark as processed in our tracking
                        pdf_file["is_processed"] = True
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
        
        # Format the result message
        if processed_count == 0:
            return "No new PDFs to process."
        else:
            return f"Processed {processed_count} PDFs. Extracted {total_edges} knowledge edges."
    
    except Exception as e:
        return f"Error processing PDFs: {str(e)}"


async def get_knowledge(include_ontology: bool = False) -> pd.DataFrame:
    """
    Get all extracted scientific knowledge as a DataFrame.
    
    Args:
        include_ontology: Whether to include ontology mapping information in the DataFrame
    """
    if not state.dependencies:
        return pd.DataFrame(columns=["Subject", "Predicate", "Object", "Evidence", "Source"])
    
    try:
        # Create RunContext
        class RunContext:
            def __init__(self, deps):
                self.dependencies = deps
                
        ctx = RunContext(state.dependencies)
        
        # Get knowledge from processing all PDF files
        all_knowledge = []
        
        # Process each PDF file in the directory
        for pdf_file in state.current_pdfs:
            file_path = pdf_file["file_path"]
            try:
                # Read the PDF
                pdf_data = await read_pdf(ctx, file_path)
                
                # Extract knowledge
                edges = await extract_knowledge(ctx, pdf_data)
                
                # Ground entities to ontologies and map predicates to biolink
                if edges:
                    processed_edges = await create_kg_edges(ctx, edges)
                    all_knowledge.extend(processed_edges)
            except Exception as e:
                print(f"Error processing {file_path} for knowledge retrieval: {str(e)}")
        
        state.extracted_knowledge = all_knowledge
        
        if not all_knowledge:
            return pd.DataFrame(columns=["Subject", "Predicate", "Object", "Evidence", "Source"])
        
        # Prepare columns based on whether to include ontology info
        if include_ontology:
            # Convert to DataFrame with ontology information
            df = pd.DataFrame([
                {
                    "Subject": k["subject"],
                    "Subject_CURIE": k.get("subject_curie", ""),
                    "Predicate": k["predicate"],
                    "Predicate_CURIE": k.get("predicate_curie", ""),
                    "Object": k["object"],
                    "Object_CURIE": k.get("object_curie", ""),
                    "Evidence": k.get("evidence_text", ""),
                    "Source": k.get("source_title", "Unknown"),
                    "DOI": k.get("source_id", ""),
                    "Confidence": k.get("confidence", 0.0)
                }
                for k in all_knowledge
            ])
        else:
            # Simple version without ontology information
            df = pd.DataFrame([
                {
                    "Subject": k["subject"],
                    "Predicate": k["predicate"],
                    "Object": k["object"],
                    "Evidence": k.get("evidence_text", ""),
                    "Source": k.get("source_title", "Unknown"),
                    "DOI": k.get("source_id", "")
                }
                for k in all_knowledge
            ])
        
        return df
    
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])


async def map_ontologies() -> Dict:
    """Map all scientific assertions to ontology terms."""
    if not state.dependencies:
        return {"status": "error", "message": "Please set up the PDF directory first."}
    
    try:
        # Create RunContext
        class RunContext:
            def __init__(self, deps):
                self.dependencies = deps
                
        ctx = RunContext(state.dependencies)
        
        # Process each knowledge item from state
        if not state.extracted_knowledge:
            # Get knowledge first if not already loaded
            all_knowledge = []
            
            # Process each PDF file in the directory
            for pdf_file in state.current_pdfs:
                file_path = pdf_file["file_path"]
                try:
                    # Read the PDF
                    pdf_data = await read_pdf(ctx, file_path)
                    
                    # Extract knowledge
                    edges = await extract_knowledge(ctx, pdf_data)
                    
                    if edges:
                        all_knowledge.extend(edges)
                except Exception as e:
                    print(f"Error processing {file_path} for knowledge retrieval: {str(e)}")
            
            state.extracted_knowledge = all_knowledge
        
        # Map each entity to ontology and each predicate to biolink
        mapped_count = 0
        unmapped_count = 0
        updated_knowledge = []
        
        for edge in state.extracted_knowledge:
            # Ground entities to ontologies
            grounded_edge = await ground_to_ontology(ctx, edge)
            
            # Map predicates to Biolink model
            mapped_edge = await map_to_biolink(ctx, grounded_edge)
            
            # Check if mapping was successful
            has_subject_mapping = "subject_curie" in mapped_edge and mapped_edge["subject_curie"]
            has_predicate_mapping = "predicate_curie" in mapped_edge and mapped_edge["predicate_curie"]
            has_object_mapping = "object_curie" in mapped_edge and mapped_edge["object_curie"]
            
            if has_subject_mapping or has_predicate_mapping or has_object_mapping:
                mapped_count += 1
            else:
                unmapped_count += 1
                
            updated_knowledge.append(mapped_edge)
        
        # Update state with mapped knowledge
        state.extracted_knowledge = updated_knowledge
        
        # Return mapping statistics
        total = len(state.extracted_knowledge)
        mapping_rate = f"{mapped_count/total*100:.1f}%" if total > 0 else "0%"
        
        return {
            "status": "success",
            "total": total,
            "mapped": mapped_count,
            "unmapped": unmapped_count,
            "mapping_rate": mapping_rate
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def export_knowledge(format_type: str) -> Dict:
    """Export scientific knowledge to a file in the specified format."""
    if not state.dependencies or not state.extracted_knowledge:
        return {"error": "No knowledge to export"}
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format_type}") as temp_file:
            file_path = temp_file.name
        
        if format_type == "json":
            with open(file_path, 'w') as f:
                json.dump(state.extracted_knowledge, f, indent=2)
                
        elif format_type == "csv":
            # Include ontology information in the CSV
            df = pd.DataFrame([
                {
                    "Subject": k["subject"],
                    "Subject_CURIE": k.get("subject_curie", ""),
                    
                    "Predicate": k["predicate"],
                    "Predicate_CURIE": k.get("predicate_curie", ""),
                    
                    "Object": k["object"],
                    "Object_CURIE": k.get("object_curie", ""),
                    
                    "Evidence": k.get("evidence_text", ""),
                    "Confidence": k.get("confidence", 0.0),
                    "Source_ID": k.get("source_id", ""),
                    "Source_Title": k.get("source_title", ""),
                }
                for k in state.extracted_knowledge
            ])
            df.to_csv(file_path, index=False)
            
        elif format_type == "kgx":
            # Create RunContext
            class RunContext:
                def __init__(self, deps):
                    self.dependencies = deps
                    
            ctx = RunContext(state.dependencies)
            
            # Use the agent's tool to export as KGX
            result = await export_to_kgx(ctx, state.extracted_knowledge, f"export.{format_type}")
            if result.get("status") != "success":
                return result
            
            # Use the path from the result
            file_path = result.get("output_path", file_path)
        
        return {"status": "success", "file_path": file_path}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def clear_cache(file_path: Optional[str] = None) -> str:
    """
    Clear the extracted knowledge cache.
    
    Args:
        file_path: Optional path to a specific PDF file to clear from cache.
                  If None, clears the entire cache.
    
    Returns:
        Message about the operation result
    """
    if not state.dependencies:
        return "Error: No cache to clear. Please set up the PDF directory first."
    
    try:
        if file_path:
            # Verify the file exists
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' does not exist."
            
            # Clear the specific file from cache
            entries_cleared = state.dependencies.clear_cache(file_path)
            
            if entries_cleared > 0:
                return f"Successfully cleared cache for '{os.path.basename(file_path)}'."
            else:
                return f"File '{os.path.basename(file_path)}' was not in the cache."
        else:
            # Clear the entire cache
            entries_cleared = state.dependencies.clear_cache()
            
            if entries_cleared > 0:
                return f"Successfully cleared the entire cache ({entries_cleared} entries)."
            else:
                return "Cache was already empty."
                
        # Update the current PDF list (processed status may have changed)
        pdf_files = []
        if os.path.exists(state.pdf_directory):
            for filename in os.listdir(state.pdf_directory):
                if filename.lower().endswith('.pdf'):
                    file_path = os.path.join(state.pdf_directory, filename)
                    is_processed = state.dependencies.is_processed(file_path)
                    pdf_files.append({
                        "file_path": file_path,
                        "filename": filename,
                        "is_processed": is_processed
                    })
        
        state.current_pdfs = pdf_files
        
    except Exception as e:
        return f"Error clearing cache: {str(e)}"


def create_demo():
    """Create the Gradio demo interface."""
    
    with gr.Blocks(title="Scientific Knowledge Extraction Agent") as demo:
        gr.Markdown("# Scientific Knowledge Extraction Agent")
        gr.Markdown("Extract and normalize scientific knowledge from research papers in PDF format.")
        
        with gr.Tab("Setup"):
            with gr.Row():
                pdf_dir_input = gr.Textbox(
                    label="PDF Directory", 
                    placeholder="Enter the full path to directory containing PDFs"
                )
                cache_dir_input = gr.Textbox(
                    label="Cache Directory (Optional)", 
                    placeholder="Leave empty for default cache location"
                )
            
            setup_button = gr.Button("Setup Directories")
            setup_output = gr.Textbox(label="Setup Result")
            
            setup_button.click(
                fn=setup_directories, 
                inputs=[pdf_dir_input, cache_dir_input], 
                outputs=setup_output
            )
        
        with gr.Tab("PDF Files"):
            pdf_refresh_button = gr.Button("Refresh PDF List")
            pdf_list = gr.DataFrame(headers=["Filename", "Processed"])
            
            with gr.Row():
                process_button = gr.Button("Process All Unprocessed PDFs")
                clear_cache_button = gr.Button("Clear Cache", variant="secondary")
                
            process_result = gr.Textbox(label="Processing Result")
            cache_result = gr.Textbox(label="Cache Operation Result")
            
            pdf_refresh_button.click(fn=get_pdf_list, inputs=[], outputs=pdf_list)
            process_button.click(fn=process_all_pdfs, inputs=[], outputs=process_result)
            clear_cache_button.click(fn=clear_cache, inputs=[], outputs=[cache_result, pdf_list])
        
        with gr.Tab("Knowledge"):
            with gr.Row():
                get_knowledge_button = gr.Button("Get Extracted Knowledge")
                include_ontology = gr.Checkbox(label="Include Ontology Mappings", value=False)
            
            knowledge_table = gr.DataFrame()
            
            get_knowledge_button.click(
                fn=get_knowledge, 
                inputs=[include_ontology], 
                outputs=knowledge_table
            )
        
        with gr.Tab("Ontology Mapping"):
            map_ontology_button = gr.Button("Map Knowledge to Ontology Terms")
            mapping_result = gr.JSON(label="Mapping Result")
            
            map_ontology_button.click(fn=map_ontologies, inputs=[], outputs=mapping_result)
            
            gr.Markdown("### Ontology Mapping Details")
            gr.Markdown("""
            The mapping process connects extracted terms to standard ontologies:
            - Gene Ontology (GO) for biological processes, cellular components, molecular functions
            - ChEBI for chemical entities 
            - Mondo Disease Ontology (MONDO) for diseases
            - Protein Ontology (PR) for proteins
            - Uberon for anatomical entities
            - Relation Ontology (RO) for relationship types
            """)
        
        with gr.Tab("Export"):
            with gr.Row():
                export_format = gr.Radio(
                    choices=["json", "csv", "kgx"], 
                    label="Export Format", 
                    value="json"
                )
                export_button = gr.Button("Export Knowledge")
            
            export_result = gr.JSON(label="Export Result")
            
            gr.Markdown("### Export Format Details")
            gr.Markdown("""
            - **JSON**: Full knowledge data including ontology mappings and all metadata
            - **CSV**: Tabular format with separate columns for entities and their ontology mappings
            - **KGX**: Knowledge Graph Exchange format with nodes and edges suitable for import into graph databases
            """)
            
            export_button.click(fn=export_knowledge, inputs=[export_format], outputs=export_result)
        
        with gr.Tab("Chat"):
            chatbot = gr.Chatbot(type="messages")
            msg = gr.Textbox(label="Message")
            clear = gr.Button("Clear")
            chat_error = gr.Textbox(label="Error")
            
            msg.submit(chat_with_agent, [msg, chatbot], [chatbot, chat_error])
            clear.click(lambda: ([], ""), outputs=[chatbot, chat_error])
    
    return demo


# For direct execution
if __name__ == "__main__":
    demo = create_demo()
    demo.launch()