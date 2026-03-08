from focused_research_agent.state import ResearchState
from focused_research_agent.services import llm_client

def generate_queries(state: ResearchState) -> dict:
    base = (state.get("scope") or state.get("question") or "").strip().lower()
    if not base:
        return {"queries": [], "status": "planned"}

    words = base.split()

    queries = list()

    # If it's a very short input like "hi" or "resp"
    if len(words) <= 2:
        queries = [
            f"meaning of {base}",
            f"{base} usage examples",
            f"{base} overview",
        ]
    else:
         # For longer questions, keep the original plus a couple variations
         queries = [
             base,
             f"{base} overview",
             f"{base} key facts",
             f"{base} examples",
         ]

    scope = (state.get("scope") or "").strip().lower()
    user_query =( state.get("question") or "").strip().lower()
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

    inputs = (
        f"SCOPE: {scope}\n"
        f"ASSUMPTIONS: {assumptions}\n"
        f"CONSTRAINTS: {constraints}"
    )

    question_scope = f"""
       {generate_queries_system_prompt}
       
       {inputs}

       User question:
       {user_query}
       """.strip()

    try:
        response = llm_client.generate_json(question_scope)
    except ValueError as e:
        response = {}



    if isinstance(response, dict) and ("queries" in response ):
        llm_queries = response.get("queries")

        if isinstance(response.get("queries"),list):
            cleaned_list = []
            for item in llm_queries:
                if isinstance(item,str):
                    item = item.strip()
                    if item:
                        cleaned_list.append(item)

            # Use LLM result only if it produced enough queries
            if len(cleaned_list) >= 3:
                queries = cleaned_list


    return {"queries": queries[:6], "status": "planned"}