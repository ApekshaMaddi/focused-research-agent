from focused_research_agent.interfaces.llm_interface import LLMProvider
from focused_research_agent.state import ResearchState



def generate_queries(state: ResearchState, llm_provider: LLMProvider) -> dict:
    base = (state.get("scope") or state.get("question") or "").strip().lower()
    if not base:
        raise ValueError("No scope or question available for generate_queries")

    scope = (state.get("scope") or "").strip().lower()
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

    Facet coverage rule (generic):
    - First, internally identify 4–6 key facets relevant to the scope.
      Examples of possible facets: overview/definition, rules/requirements, limits/edge cases,
      steps/how-to, costs/fees, risks/pitfalls, tax/legal, examples/case studies, recent updates.
    - Then produce queries so each query focuses on a different facet (avoid duplicates).

    Use provided inputs:
    - If constraints include geography/time, include those terms in relevant queries.
    - Keep each query short (typically 5–10 words).

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

    response = llm_provider.generate_json(question_scope)

    if isinstance(response, dict) and ("queries" in response):
        llm_queries = response["queries"]
    else:
        raise ValueError(
            "Invalid response or invalid queries format received from generate json"
        )

    if isinstance(llm_queries, list):
        cleaned_list = []
    else:
        raise ValueError("Invalid response from generate json")

    for item in llm_queries:
        if isinstance(item, str):
            item = item.strip()
        else:
            raise ValueError("Queries does not contains string")
        if item:
            cleaned_list.append(item)

    if len(cleaned_list) < 3:
        raise ValueError("generate_queries: LLM returned fewer than 3 valid queries")

    queries = cleaned_list

    return {"queries": queries[:6], "status": "planned"}
