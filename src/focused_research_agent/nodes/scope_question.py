from focused_research_agent.interfaces.llm_interface import LLMProvider
from focused_research_agent.state import ResearchState


def scope_question(state: ResearchState, llm_provider: LLMProvider) -> dict:

    user_query = (state.get("question") or "").strip()

    if not user_query:
        return {"errors": ["scope_question: No user query provided"]}

    scope_question_system_prompt = """
    Return ONLY valid JSON. No markdown. No backticks. No extra text.

    The JSON MUST have exactly these keys:
    - scope (string)
    - assumptions (list of 2 to 5 short strings)
    - constraints (dict, can be empty {})

    Example JSON output:
    {
      "scope": "Explain how RESP works in Canada: contributions, grants, withdrawals, common pitfalls",
      "assumptions": ["User is a beginner", "Canada context"],
      "constraints": {"geography": "Canada", "time_range": "current", "depth": "intro"}
    }
    """.strip()

    question_scope = f"""
    {scope_question_system_prompt}

    User question:
    {user_query}
    """.strip()

    try:
        response = llm_provider.generate_json(question_scope)
    except Exception as e:
        return {"errors": [f"scope_question failed: {e}"]}

    if not isinstance(response, dict):
        return {"errors": ["scope_question: Invalid response type received from LLM"]}

    if not all(key in response for key in ("scope", "assumptions", "constraints")):
        return {"errors": ["scope_question: Missing required keys in LLM response"]}

    scope = response.get("scope")
    assumptions = response.get("assumptions")
    constraints = response.get("constraints")

    if not isinstance(scope, str) or not scope.strip():
        return {"errors": ["scope_question: 'scope' must be a non-empty string"]}

    if not isinstance(assumptions, list):
        return {"errors": ["scope_question: 'assumptions' must be a list"]}

    cleaned_assumptions = []

    for item in assumptions:
        if not isinstance(item, str) or not item.strip():
            return {
                "errors": ["scope_question: Assumptions must contain non-empty strings"]
            }

        cleaned_assumptions.append(item.strip())

    if len(cleaned_assumptions) < 2 or len(cleaned_assumptions) > 5:
        return {"errors": ["scope_question: 'assumptions' must contain 2 to 5 items"]}

    if not isinstance(constraints, dict):
        return {"errors": ["scope_question: 'constraints' must be a dict"]}

    return {
        "scope": scope.strip(),
        "assumptions": cleaned_assumptions,
        "constraints": constraints,
        "status": "scoped",
    }
