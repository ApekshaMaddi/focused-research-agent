from focused_research_agent.state import ResearchState


def finalize_run(state: ResearchState) -> dict:
    """Mark the run as completed or failed based on final state.

    Args:
    state: The current research state.

    Returns:
    dict: A partial state update containing the final status.
    """
    errors = state.get("errors") or []
    answer = (state.get("answer") or "").strip()

    if errors or not answer:
        return {"status": "error"}

    return {"status": "completed"}
