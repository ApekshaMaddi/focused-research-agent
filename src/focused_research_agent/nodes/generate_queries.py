from focused_research_agent.interfaces.llm_interface import LLMProvider
from focused_research_agent.state import ResearchState


def generate_queries(state: ResearchState, llm_provider: LLMProvider) -> dict:
    """Generate focused web-search queries from the scoped question.

    This node uses the LLM provider to produce 3 to 6 short,
    search-engine-style queries that directly support answering the
    user's question.

    Args:
        state: The current research state.
        llm_provider: The active LLM provider instance.

    Returns:
        dict: A partial state update containing generated queries and
        status, or an errors field if generation fails.
    """
    base = (state.get("scope") or state.get("question") or "").strip()

    if not base:
        return {"errors": ["generate_queries: No scope or question available"]}

    scope = (state.get("scope") or "").strip()
    user_query = (state.get("question") or "").strip()
    assumptions = state.get("assumptions") or []
    constraints = state.get("constraints") or {}

    generate_queries_system_prompt = """
    Return ONLY valid JSON. No markdown. No backticks. No extra text.
    Return EXACTLY one key: "queries".

    Task:
    - Generate 3 to 6 search-engine style queries (Google-style phrases).
    - Do NOT repeat the scope sentence verbatim as a query.
    - Queries must be diverse: each query should target a different facet of the topic.
    - Every query must directly help answer the user's specific question.
    - Do NOT generate queries about the general topic area if they do not help answer what the user actually asked.

    Facet coverage rule:
    - First, internally identify 4 to 6 key facets relevant to the scope and user question.
    - Then produce queries so each query focuses on a different facet.

    Use provided inputs:
    - If constraints include geography or time, include those terms in relevant queries.
    - Keep each query short (typically 5 to 10 words).

    Output JSON schema:
    {
      "queries": ["query 1", "query 2", "query 3"]
    }
    """.strip()

    inputs = f"SCOPE: {scope}\nASSUMPTIONS: {assumptions}\nCONSTRAINTS: {constraints}"

    question_scope = f"""
    {generate_queries_system_prompt}

    {inputs}

    User question:
    {user_query}
    """.strip()

    try:
        response = llm_provider.generate_json(question_scope)
    except Exception as e:
        return {"errors": [f"generate_queries failed: {e}"]}

    if not isinstance(response, dict) or "queries" not in response:
        return {"errors": ["generate_queries: Invalid response received from LLM"]}

    llm_queries = response["queries"]

    if not isinstance(llm_queries, list):
        return {"errors": ["generate_queries: 'queries' must be a list"]}

    cleaned_list = []

    for item in llm_queries:
        if not isinstance(item, str):
            return {"errors": ["generate_queries: Query item must be a string"]}

        item = item.strip()

        if item:
            cleaned_list.append(item)

    if len(cleaned_list) < 3:
        return {"errors": ["generate_queries: LLM returned fewer than 3 valid queries"]}

    return {
        "queries": cleaned_list[:6],
        "status": "planned",
    }
