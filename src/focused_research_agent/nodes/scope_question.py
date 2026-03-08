from focused_research_agent.state import ResearchState
from focused_research_agent.services import llm_client



def scope_question(state: ResearchState)->dict:

    user_query = (state.get("question") or "").strip()

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
        response = llm_client.generate_json(question_scope)
    except ValueError as e:
        response = {}



    scope = f"Research and summarize: {user_query}"
    scope_assumptions = []
    scope_constraints = {}

    if isinstance(response,dict) and ("scope" in response ) and ("assumptions" in response) and ("constraints" in response):
        if isinstance(response.get("scope"),str) and isinstance(response.get("assumptions"),list) and isinstance(response.get("constraints"),dict):
            scope = response.get("scope")
            scope_assumptions = response.get("assumptions")
            scope_constraints = response.get("constraints")

    return{
        "scope":scope,
        "assumptions": scope_assumptions,
        "constraints": scope_constraints,
        "status": "scoped",
    }
