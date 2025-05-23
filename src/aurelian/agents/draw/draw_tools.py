"""
Tools for the draw agent.
"""
import base64
from typing import Optional
import cairosvg
from pydantic import BaseModel

from pydantic_ai import RunContext, BinaryContent, ModelRetry

from aurelian.agents.draw.draw_config import DrawDependencies


class DrawingFeedback(BaseModel):
    """
    Feedback on the drawing's clarity and simplicity.
    """
    feedback: str
    necessary_changes: Optional[str] = None
    optional_changes: Optional[str] = None




async def convert_svg_to_png(ctx: RunContext[DrawDependencies], svg_content: str) -> bytes:
    """
    Convert SVG content to PNG image.

    Args:
        ctx: The run context
        svg_content: SVG markup as a string
        
    Returns:
        bytes: PNG image data
    """
    print("Converting SVG to PNG")
    
    # Check size limits
    if len(svg_content.encode('utf-8')) > ctx.deps.max_svg_size:
        raise ValueError(f"SVG content exceeds maximum size of {ctx.deps.max_svg_size} bytes")
    
    # Convert SVG to PNG using cairosvg
    png_bytes = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
    return png_bytes


async def svg_to_data_url(ctx: RunContext[DrawDependencies], svg_content: str) -> str:
    """
    Convert SVG content to a data URL for embedding in HTML.

    Args:
        ctx: The run context
        svg_content: SVG markup as a string
        
    Returns:
        str: Data URL representation of the SVG
    """
    print("Converting SVG to data URL")
    
    # Check size limits
    if len(svg_content.encode('utf-8')) > ctx.deps.max_svg_size:
        raise ValueError(f"SVG content exceeds maximum size of {ctx.deps.max_svg_size} bytes")
    
    # Encode as base64 and create data URL
    b64_svg = base64.b64encode(svg_content.encode('utf-8')).decode('ascii')
    return f"data:image/svg+xml;base64,{b64_svg}"


async def judge_drawing(ctx: RunContext[DrawDependencies], 
                        svg_content: str, 
                        description: str,
                        attempt_number: int = 1) -> DrawingFeedback:
    """
    Judge the readability of an SVG drawing based on the description.

    In particular, make sure that text is readable and contained within boxes
    
    Args:
        ctx: The run context
        svg_content: SVG markup as a string
        description: Simple natural language narrative summary of the drawing
        attempt_number: The attempt number for the drawing
        
    Returns:
        DrawingFeedback: Feedback on the drawing's readability
    """
    print(f"Judging drawing for: {description}")
    
    from aurelian.agents.draw.judge_agent import drawing_judge_agent
    
    # Convert to PNG for the judge to see
    png_bytes = await convert_svg_to_png(ctx, svg_content)
    img = BinaryContent(data=png_bytes, media_type='image/png')
    
    # Get feedback from judge
    feedback = await drawing_judge_agent.run(
        [f"Please evaluate this drawing based on this description: {description} (this is attempt #{attempt_number})", img],
        deps=ctx.deps)
    
    return feedback.data