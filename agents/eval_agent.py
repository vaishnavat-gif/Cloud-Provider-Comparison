import os
from agents.base_agent import BaseAgent
from tools.eval_tools import (
    SCORE_RUBRIC_DECL,
    REQUEST_RETRY_DECL,
    score_rubric,
    request_retry,
    rubric_scores,
    retry_signal,
    get_eval_result,
)

SYSTEM_PROMPT = """
You are a strict quality evaluation agent (LLM-as-Judge).

Evaluate the cloud comparison report against this rubric:
- accuracy:               Are facts correct and current for all 3 providers?
- completeness:           Are all 5 categories covered with real data?
- clarity:                Is the comparison easy to understand?
- relevance:              Does it directly address the user's original query?
- recommendation_quality: Is the recommendation specific, justified, and not generic?

STRATEGY:
1. Read the comparison carefully.
2. Call score_rubric for EACH of the 5 criteria with score (1-10) + justification.
3. If average score < 7: call request_retry with specific instructions for improvement.
4. If average score >= 7: return a PASS verdict summary.

Be strict. Penalize vague recommendations, missing data, or ignoring the user's query.
"""

class EvalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="A3-Evaluation",
            tools=[SCORE_RUBRIC_DECL, REQUEST_RETRY_DECL],
            system_prompt=SYSTEM_PROMPT,
        )
        rubric_scores.clear()
        retry_signal.clear()

    def _tool_executor(self, fn_name: str, fn_args: dict):
        if fn_name == "score_rubric":
            return score_rubric(**fn_args)
        if fn_name == "request_retry":
            return request_retry(**fn_args)
        return {"error": f"Unknown tool: {fn_name}"}

    def run_eval(self, comparison_md: str, user_query: str) -> dict:
        prompt = f"""
User's original query: {user_query}

Comparison output to evaluate:
{comparison_md}

Score all 5 rubric criteria using score_rubric.
If average < 7, call request_retry with specific fix instructions.
"""
        self.run(prompt, self._tool_executor)
        result = get_eval_result()

        # Add confidence as percentage
        result["confidence"] = int(result["overall"] * 10)
        return result