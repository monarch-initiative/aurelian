"""
Tools for the SPIRES agent.
"""
import logging
from typing import Any, Dict, Optional, List
from pathlib import Path

from pydantic_ai import RunContext, ModelRetry
from pydantic import BaseModel

from .spires_config import SPIRESDependencies

logger = logging.getLogger(__name__)


class ExtractedKnowledge(BaseModel):
    """Structured knowledge extracted by SPIRES."""
    template_used: str
    extracted_data: Dict[str, Any]
    text_length: int
    chunks_processed: int
    grounded_entities: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None


def get_spires_engine(ctx: RunContext[SPIRESDependencies]):
    """Get or create a SPIRES engine instance."""
    try:
        from ontogpt.engines.spires_engine import SPIRESEngine
        from ontogpt.io.template_loader import get_template_details
        
        # Get template details
        template_details = get_template_details(template=ctx.deps.template_name)
        
        # Create engine with configuration
        engine = SPIRESEngine(
            template_details=template_details,
            **ctx.deps.get_engine_kwargs()
        )
        
        return engine, template_details
        
    except ImportError as e:
        raise ModelRetry(f"OntoGPT not installed. Please install with: pip install ontogpt. Error: {str(e)}")
    except Exception as e:
        raise ModelRetry(f"Error initializing SPIRES engine: {str(e)}")


async def extract_knowledge_from_text(
    ctx: RunContext[SPIRESDependencies],
    text: str,
    template: Optional[str] = None,
    enable_grounding: Optional[bool] = None,
    chunk_by_sentence: Optional[bool] = None,
) -> ExtractedKnowledge:
    """
    Extract structured knowledge from text using SPIRES/OntoGPT.

    Args:
        ctx: The run context
        text: Text to extract knowledge from
        template: Optional template override (defaults to config template)
        enable_grounding: Optional grounding override (defaults to config setting)
        chunk_by_sentence: Optional chunking override (defaults to config setting)

    Returns:
        ExtractedKnowledge object with structured data and metadata
    """
    try:
        # Override template if provided
        if template:
            original_template = ctx.deps.template_name
            ctx.deps.template_name = template
        
        engine, template_details = get_spires_engine(ctx)
        
        # Restore original template
        if template:
            ctx.deps.template_name = original_template
        
        # Use config defaults or overrides
        should_ground = enable_grounding if enable_grounding is not None else ctx.deps.enable_grounding
        should_chunk = chunk_by_sentence if chunk_by_sentence is not None else ctx.deps.chunk_by_sentence
        
        chunks_processed = 1
        
        # Handle large texts by chunking
        if should_chunk and len(text) > ctx.deps.max_tokens * 4:  # Rough token estimate
            logger.info(f"Text is large ({len(text)} chars), chunking by sentences")
            sentences = engine.chunk_text_by_sentence(text, max_tokens=ctx.deps.max_tokens)
            chunks_processed = len(sentences)
            
            # Process each chunk and merge results
            all_results = []
            for i, chunk in enumerate(sentences):
                logger.info(f"Processing chunk {i+1}/{len(sentences)}")
                result = engine.extract_from_text(chunk)
                all_results.append(result)
            
            # Merge results (this is template-specific, but we'll do a basic merge)
            extracted_data = engine.merge_results(all_results) if hasattr(engine, 'merge_results') else all_results[0]
        else:
            # Process text directly
            extracted_data = engine.extract_from_text(text)
        
        # Ground entities if requested
        grounded_entities = None
        if should_ground and hasattr(engine, 'ground_annotation_object'):
            try:
                logger.info("Grounding entities to ontologies...")
                grounded_entities = engine.ground_annotation_object(extracted_data)
            except Exception as e:
                logger.warning(f"Entity grounding failed: {str(e)}")
        
        return ExtractedKnowledge(
            template_used=ctx.deps.template_name,
            extracted_data=extracted_data.dict() if hasattr(extracted_data, 'dict') else extracted_data,
            text_length=len(text),
            chunks_processed=chunks_processed,
            grounded_entities=grounded_entities.dict() if grounded_entities and hasattr(grounded_entities, 'dict') else grounded_entities,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error extracting knowledge: {str(e)}")
        return ExtractedKnowledge(
            template_used=ctx.deps.template_name,
            extracted_data={},
            text_length=len(text),
            chunks_processed=0,
            success=False,
            error_message=str(e)
        )


async def list_available_templates(
    ctx: RunContext[SPIRESDependencies]
) -> Dict[str, str]:
    """
    List all available OntoGPT templates.

    Args:
        ctx: The run context

    Returns:
        Dictionary mapping template names to descriptions
    """
    
    from ontogpt.io.template_loader import get_all_templates
    templates = get_all_templates()
    result = {}
    for template_name in templates:
        try:
            from ontogpt.io.template_loader import get_template_details
            details = get_template_details(template=template_name)
            description = getattr(details, 'description', 'No description available')
            result[template_name] = description
        except Exception:
            result[template_name] = "Template available (no description)"
    
    return result


async def query_paperqa_and_extract(
    ctx: RunContext[SPIRESDependencies],
    query: str,
    template: Optional[str] = None,
    enable_grounding: Optional[bool] = None,
) -> ExtractedKnowledge:
    """
    Query PaperQA for papers and extract structured knowledge using SPIRES.
    
    This is the key integration function that connects PaperQA with SPIRES.

    Args:
        ctx: The run context
        query: Query to search papers for
        template: Optional template override
        enable_grounding: Optional grounding override

    Returns:
        ExtractedKnowledge object with structured data from papers
    """
    if not ctx.deps.paperqa_deps:
        raise ModelRetry("PaperQA dependencies not configured. Set paperqa_deps in SPIRESDependencies.")
    
    try:
        # Import PaperQA tools
        from aurelian.agents.paperqa.paperqa_tools import query_papers
        from pydantic_ai import RunContext as PQARunContext
        
        # Create PaperQA context
        pqa_ctx = PQARunContext(deps=ctx.deps.paperqa_deps)
        
        logger.info(f"Querying PaperQA with: {query}")
        
        # Query papers using PaperQA
        papers_result = await query_papers(pqa_ctx, query)
        
        # Check if we got results
        if not papers_result or not hasattr(papers_result, 'data'):
            return ExtractedKnowledge(
                template_used=template or ctx.deps.template_name,
                extracted_data={},
                text_length=0,
                chunks_processed=0,
                success=False,
                error_message="No papers found or PaperQA returned empty result"
            )
        
        # Extract text content from PaperQA result
        if hasattr(papers_result.data, 'answer'):
            text_content = papers_result.data.answer
        elif hasattr(papers_result, 'answer'):
            text_content = papers_result.answer
        elif isinstance(papers_result, str):
            text_content = papers_result
        else:
            text_content = str(papers_result)
        
        logger.info(f"Extracted {len(text_content)} characters from PaperQA")
        
        # Now extract structured knowledge using SPIRES
        logger.info("Extracting structured knowledge with SPIRES...")
        knowledge = await extract_knowledge_from_text(
            ctx, 
            text_content, 
            template=template, 
            enable_grounding=enable_grounding
        )
        
        # Add PaperQA metadata
        if hasattr(knowledge, 'extracted_data') and isinstance(knowledge.extracted_data, dict):
            knowledge.extracted_data['paperqa_query'] = query
            knowledge.extracted_data['paperqa_result_length'] = len(text_content)
        
        return knowledge
        
    except Exception as e:
        logger.error(f"Error in PaperQA + SPIRES integration: {str(e)}")
        return ExtractedKnowledge(
            template_used=template or ctx.deps.template_name,
            extracted_data={},
            text_length=0,
            chunks_processed=0,
            success=False,
            error_message=f"Integration error: {str(e)}"
        )


async def extract_from_file(
    ctx: RunContext[SPIRESDependencies],
    file_path: str,
    template: Optional[str] = None,
    enable_grounding: Optional[bool] = None,
) -> ExtractedKnowledge:
    """
    Extract structured knowledge from a file using SPIRES.

    Args:
        ctx: The run context
        file_path: Path to the file to process
        template: Optional template override
        enable_grounding: Optional grounding override

    Returns:
        ExtractedKnowledge object with structured data
    """
    try:
        file_path_obj = Path(file_path)
        
        # Check if file exists
        if not file_path_obj.exists():
            # Try relative to workdir
            workdir_path = Path(ctx.deps.workdir.location) / file_path
            if workdir_path.exists():
                file_path_obj = workdir_path
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        if file_path_obj.suffix.lower() == '.pdf':
            # Handle PDF files
            try:
                import PyPDF2
                with open(file_path_obj, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text_content = ""
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
            except ImportError:
                raise ModelRetry("PyPDF2 not installed. Install with: pip install PyPDF2")
        else:
            # Handle text files
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                text_content = f.read()
        
        logger.info(f"Read {len(text_content)} characters from {file_path_obj}")
        
        # Extract knowledge
        knowledge = await extract_knowledge_from_text(
            ctx, 
            text_content, 
            template=template, 
            enable_grounding=enable_grounding
        )
        
        # Add file metadata
        if hasattr(knowledge, 'extracted_data') and isinstance(knowledge.extracted_data, dict):
            knowledge.extracted_data['source_file'] = str(file_path_obj)
            knowledge.extracted_data['file_size'] = file_path_obj.stat().st_size
        
        return knowledge
        
    except Exception as e:
        logger.error(f"Error extracting from file {file_path}: {str(e)}")
        return ExtractedKnowledge(
            template_used=template or ctx.deps.template_name,
            extracted_data={},
            text_length=0,
            chunks_processed=0,
            success=False,
            error_message=f"File processing error: {str(e)}"
        )


async def change_template(
    ctx: RunContext[SPIRESDependencies],
    template_name: str
) -> Dict[str, Any]:
    """
    Change the active template for knowledge extraction.

    Args:
        ctx: The run context
        template_name: Name of the template to switch to

    Returns:
        Status information about the template change
    """
    try:
        from ontogpt.io.template_loader import get_template_details
        
        # Validate template exists
        template_details = get_template_details(template=template_name)
        
        # Update configuration
        old_template = ctx.deps.template_name
        ctx.deps.template_name = template_name
        
        return {
            "success": True,
            "old_template": old_template,
            "new_template": template_name,
            "template_description": getattr(template_details, 'description', 'No description available'),
            "message": f"Successfully changed template from {old_template} to {template_name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to change template to {template_name}: {str(e)}"
        }