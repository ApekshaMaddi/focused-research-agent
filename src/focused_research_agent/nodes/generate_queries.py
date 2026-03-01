from focused_research_agent.state import ResearchState

def generate_queries(state: ResearchState) -> dict:
    base = (state.get("scope") or state.get("question") or "").strip().lower()

    if not base:
        return {"queries": [], "status": "planned"}

    words = base.split()

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

    return {"queries": queries[:4], "status": "planned"}