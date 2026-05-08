
import logging
from focused_research_agent.state import ResearchState

logger = logging.getLogger(__name__)

def finalize_run(state: ResearchState) -> dict:
    """Mark the run as completed or failed based on final state.

    Args:
    state: The current research state.

    Returns:
    dict: A partial state update containing the final status.
    """
    errors = state.get("errors") or []
    answer = (state.get("answer") or "").strip()
    run_id = state.get("run_id", "unknown")

    if errors or not answer:
        logger.error( 
            "Run finalized with error. run_id=%s errors=%s",
            run_id,
            errors,
        )
        return {"status": "error"}
    logger.info("Run completed successfully. run_id=%s", run_id)
    return {"status": "completed"}
