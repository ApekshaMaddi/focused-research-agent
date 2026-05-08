"""
Run initialization node for the Focused Research Agent.

This module contains the entry node for the LangGraph research workflow.
It generates a unique run ID and validates that a user question is present
before any other node executes. If no question is found, an error is
recorded in state and the graph routes to handle_error.
"""

import logging
import uuid

from focused_research_agent.state import ResearchState

logger = logging.getLogger(__name__)


def initialize_state(state: ResearchState) -> dict:
    """
    Initializes a new research run. Generates a unique run ID
    and validates that a question was provided.
    """
    run_id = str(uuid.uuid4())
    user_query = (state.get("question") or "").strip()
    errors = []

    if not user_query:
        logger.error("init_run: No question provided")
        errors.append("init_run: No question provided")
    else:
        logger.info(
            "Research run started. run_id=%s question='%s'", run_id, user_query[:50]
        )

    return {
        "run_id": run_id,
        "status": "started",
        "errors": errors,
    }
