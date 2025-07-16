import warnings
from typing import Any

from pydantic_evals.evaluators import Evaluator, EvaluatorContext
from aurelian.agents.knowledge_agent.knowledge_agent_models import ExtractionResult, \
    SimpleEntity


class SimpleEntityEvaluator(Evaluator[SimpleEntity, ExtractionResult]):
    """
    Custom evaluator for knowledge agent

    This evaluator checks if the expected entity is in the extraction result
    """

    def evaluate(self, ctx: EvaluatorContext[Any, Any]) -> float:
        """
        Evaluate GO-CAM agent response by checking for expected substring.

        Args:
            ctx: The evaluator context containing input, output, and expected output

        Returns:
            Score between 0.0 and 1.0 (1.0 = pass, 0.0 = fail)
        """
        # If no expected output is specified, return 1.0 (success)
        if ctx.expected_output is None:
            return 1.0

        # loop over ctx.output.entities
        if isinstance(ctx.output, ExtractionResult):
            for entity in ctx.output.entities:
                # Check if the entity matches the expected output

                # for each key in dict, check that the entity has the expected value.
                # if true for all keys, then return 1.0
                result = 1.0 if all(
                           hasattr(entity, k) and getattr(entity, k) == v for k, v in
                           ctx.expected_output.items()) else 0.0
                return result
            return 0.0
        else:
            warnings.warn(f"Expected output should be of type ExtractionResult, got {type(ctx.output)}")
            return 0.0
