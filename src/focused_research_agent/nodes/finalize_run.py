from focused_research_agent.state import ResearchState


def finalize_run(state: ResearchState) -> dict:
    errors = state.get("errors") or []
    answer = (state.get("answer") or "").strip()

    if errors or not answer:
        return {"status": "error"}

    return {"status": "completed"}
