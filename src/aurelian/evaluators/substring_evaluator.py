from pydantic_evals.evaluators import Evaluator, EvaluatorContext


class SubstringEvaluator(Evaluator[str, str]):
    """
    Custom evaluator for GO-CAM agent responses.

    This evaluator checks if the expected substring is present in the agent's response.
    If no expected output is specified, it assumes the test passes (for cases where we
    only want to verify the agent doesn't error out).
    """

    def evaluate(self, ctx: EvaluatorContext[str, str]) -> float:
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

        # Check if expected string is in output
        if ctx.expected_output.lower() in ctx.output.lower():
            return 1.0
        return 0.0