from focused_research_agent.state import ResearchState
import uuid

def initialize_state(state: ResearchState) -> dict:
    run_id = str(uuid.uuid4())

    errors = state.get("errors") or list()
    user_query = (state.get("question") or "").strip()

    if not user_query:
        errors.append("No question provided")

    return{
        "run_id": run_id,
        "status": "started",
        "errors": errors,
    }



