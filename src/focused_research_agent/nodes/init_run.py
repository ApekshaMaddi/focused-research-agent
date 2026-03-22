from focused_research_agent.state import ResearchState
import uuid


def initialize_state(state: ResearchState) -> dict:
    """
    Initializes a new research run. Generates a unique run ID
    and validates that a question was provided.
    """
    run_id = str(uuid.uuid4())
    user_query = (state.get("question") or "").strip()
    errors = []

    if not user_query:
        errors.append("init_run: No question provided")

    return {
        "run_id": run_id,
        "status": "started",
        "errors": errors,
    }