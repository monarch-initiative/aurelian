"""
Agent specifically for judging the quality of drawings.
"""

from pydantic_ai import Agent

from aurelian.agents.draw.draw_tools import DrawingFeedback

# Separate agent for judging drawings
drawing_judge_agent = Agent(
    model='openai:gpt-4o',
    system_prompt="""You role is to judge the simplicity and clarity of drawings and figures.
    
    Specifically, in addition to correctness, you should focus on mistakes made, overlapping
    or unclear text, etc
    """,
    result_type=DrawingFeedback,
)