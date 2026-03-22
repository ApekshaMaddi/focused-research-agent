from focused_research_agent.state import ResearchState
import logging

logger = logging.getLogger(__name__)


def handle_error(state: ResearchState) -> dict:
    """
    Terminal error node. Logs all recorded errors and marks
    the run as failed. Reached via conditional routing when
    any upstream node records an error.
    """
    errors = state.get("errors") or []
    for error in errors:
        logger.error(error)
    return {"status": "error"}
