SCORE_RUBRIC_DECL = {
    "name": "score_rubric",
    "description": "Score one evaluation criterion from 1-10. Call for each criterion.",
    "parameters": {
        "type": "object",
        "properties": {
            "criterion": {
                "type": "string",
                "enum": [
                    "accuracy",
                    "completeness",
                    "clarity",
                    "relevance",
                    "recommendation_quality",
                ],
            },
            "score": {"type": "integer", "minimum": 1, "maximum": 10},
            "justification": {"type": "string"},
        },
        "required": ["criterion", "score", "justification"],
    },
}

REQUEST_RETRY_DECL = {
    "name": "request_retry",
    "description": "Call this if overall quality is below 7.",
    "parameters": {
        "type": "object",
        "properties": {
            "reason": {"type": "string"},
            "instructions": {"type": "string"},
        },
        "required": ["reason", "instructions"],
    },
}

rubric_scores: dict[str, dict[str, str | int]] = {}
retry_signal: dict[str, str | bool] = {}


def score_rubric(criterion: str, score: int, justification: str) -> str:
    rubric_scores[criterion] = {"score": score, "justification": justification}
    return f"Scored {criterion}: {score}/10"


def request_retry(reason: str, instructions: str) -> str:
    retry_signal.update({"retry": True, "reason": reason, "instructions": instructions})
    return "Retry signal set."


def get_eval_result() -> dict[str, object]:
    scores = [int(value["score"]) for value in rubric_scores.values()]
    overall = round(sum(scores) / len(scores), 1) if scores else 0
    return {
        "scores": rubric_scores,
        "overall": overall,
        "verdict": "PASS" if overall >= 7 else "FAIL",
        "retry": retry_signal,
    }
