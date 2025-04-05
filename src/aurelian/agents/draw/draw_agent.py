"""
Agent for creating SVG drawings based on text descriptions.
"""
from pydantic import BaseModel

from aurelian.agents.draw.draw_config import DrawDependencies
from aurelian.agents.draw.draw_tools import (
    judge_drawing, DrawingFeedback
)
from pydantic_ai import Agent, Tool

SYSTEM = """
You are an expert scientific artist specializing in creating clear illustrations and figures.

When creating SVG drawings:
1. Focus on clarity and simplicity over excessive detail
2. Use appropriate shapes, lines, and basic colors
3. Ensure the drawing is recognizable and representative of the description
4. Use valid SVG syntax with width and height attributes

ALWAYS `judge_drawing` to get feedback on your drawings, iterate on them, and improve clarity.
Even if you think you have the correct drawing, you MUST call this AT LEAST once to get a second
opinion and to make sure it renders OK.
"""

class SVGDrawing(BaseModel):
    svg_content: str
    legend: str
    feedback: DrawingFeedback

draw_agent = Agent(
    model="openai:gpt-4o",
    deps_type=DrawDependencies,
    system_prompt=SYSTEM,
    result_type=SVGDrawing,
    tools=[
        Tool(judge_drawing),
    ]
)
