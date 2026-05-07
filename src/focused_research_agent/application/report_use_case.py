"""
Application-layer report use case for the Focused Research Agent.

This module contains the application-level logic for executing the
report generation use case. It sits alongside research_use_case.py
and chat_use_case.py — same layer, same pattern, but configured for
deep research and structured long-form output.

Key differences from research_use_case.py:
- Sets mode='report' in the initial state
- Calls build_graph(search_depth='advanced') for deeper Tavily search
- Persists the completed report to SQLite

Key differences from chat_use_case.py:
- Single-turn only — no conversation threading
- No conversation_id management
- No history fetching

Architecturally, this module belongs to the application layer. It
coordinates use-case execution while keeping transport, database,
and graph concerns cleanly separated.
"""

import logging
import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from focused_research_agent.application.exceptions import ApplicationError
from focused_research_agent.application.question_validation import (
    validate_and_clean_question,
)
from focused_research_agent.application.research_use_case import (
    make_initial_state,
    normalize_state,
)
from focused_research_agent.database.repository import save_run
from focused_research_agent.graph import build_graph

logger = logging.getLogger(__name__)


def execute_report(question: str, db: Session) -> dict:
    """
    Execute a deep research report generation run.

    Validates the question, builds the graph with advanced search depth,
    invokes the research workflow in report mode, persists the result,
    and returns a normalized result dict.

    Persistence failure does not fail the report result — the completed
    report is always returned even if saving to the database fails.

    Args:
        question: User research question for the report.
        db: Active SQLAlchemy database session.

    Returns:
        dict: Normalized research result with structured markdown answer.

    Raises:
        ApplicationError: If the question fails validation.
    """
    try:
        user_query = validate_and_clean_question(question)
    except ValueError as exc:
        raise ApplicationError(str(exc)) from exc

    initial_state = make_initial_state(user_query)
    initial_state["mode"] = "report"

    graph = build_graph(search_depth="advanced")
    final_state = graph.invoke(initial_state)

    result = normalize_state(final_state, user_query)

    try:
        conversation_id = str(uuid.uuid4())
        save_run(db, result, conversation_id, turn_number=1, mode="report")
    except SQLAlchemyError:
        logger.exception("Failed to save report run to database")

    return result
