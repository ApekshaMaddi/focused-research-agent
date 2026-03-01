from focused_research_agent.state import ResearchState

def scope_question(state: ResearchState)->dict:
    user_query = (state.get("question") or "").strip()

    if user_query:
        question_scope = f"Research and summarize: {user_query}"
    else:
        question_scope = None

    return{
        "scope":question_scope,
        "assumptions": [],
        "constraints": {},
        "status": "scoped",
    }
