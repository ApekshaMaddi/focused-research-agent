from focused_research_agent.interfaces.llm_interface import LLMProvider
from focused_research_agent.state import ResearchState


def scope_question(state: ResearchState, llm_provider: LLMProvider) -> dict:

    user_query = (state.get("question") or "").strip()

    if not user_query:
        raise ValueError("No user query provided!")

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

        if (
            isinstance(response, dict)
            and ("scope" in response)
            and ("assumptions" in response)
            and ("constraints" in response)
        ):
            if (
                isinstance(response.get("scope"), str)
                and isinstance(response.get("assumptions"), list)
                and isinstance(response.get("constraints"), dict)
            ):
                scope = response.get("scope")
                scope_assumptions = response.get("assumptions")
                scope_constraints = response.get("constraints")
            else:
                return {"errors": [f"scope_question failed: {e}"]}
        else:
            return {"errors": [f"scope_question failed: {e}"]}
    except Exception as e:
        return {"errors": [f"scope_question failed: {e}"]}

    return {
        "scope": scope,
        "assumptions": scope_assumptions,
        "constraints": scope_constraints,
        "status": "scoped",
    }
