"""
Application-layer chat use case for the Focused Research Agent.

This module contains the application-level logic for executing the
conversation-aware research use case. It sits alongside
research_use_case.py — same layer, same pattern, but with
conversation threading added before and after graph execution.

Before invoking the graph, it fetches prior conversation turns from
SQLite and populates conversation_history in the initial state.
After the graph returns, it persists the completed run to SQLite.

The graph itself is identical to the single-turn research flow.
The conversation awareness lives entirely in this layer and in
synthesize_answer's prompt building — not in the graph structure.

Architecturally, this module belongs to the application layer. It
coordinates use-case execution while keeping terminal, HTTP, and
database concerns out of the core execution path.
"""

import uuid
import logging

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
from focused_research_agent.database.repository import (
    get_conversation_history,
    save_run,
)
from focused_research_agent.graph import build_graph
from focused_research_agent.state import ResearchState

logger = logging.getLogger(__name__)
MAX_HISTORY_TURNS = 5


def _build_chat_initial_state(
    question: str, conversation_id: str, conversation_history: list[dict] | None
) -> ResearchState:
    """
    Build the initial graph state for a conversation-aware research run.

    Extends the base initial state with conversation_id and
    conversation_history fields needed for context threading.

    Args:
        question: Cleaned user research question.
        conversation_id: UUID string identifying the conversation.
        conversation_history: Prior turns fetched from the database,
            or None for the first turn of a new conversation.

    Returns:
        ResearchState: Initial state with conversation context populated.
    """
    state = make_initial_state(question)
    state["conversation_id"] = conversation_id
    state["conversation_history"] = conversation_history
    state["mode"] = "research"
    return state


def execute_chat_turn(db: Session, conversation_id: str | None, question: str) -> dict:
    """
    Execute one turn of a conversation-aware research session.

    Validates the question, resolves or creates a conversation ID,
    fetches prior turns from the database for context threading,
    invokes the research graph, persists the result, and returns
    a normalized result with conversation metadata attached.

    Persistence failure does not fail the research result — the
    completed answer is always returned even if saving to the
    database fails.

    Args:
        question: User research question for this turn.
        conversation_id: Existing conversation UUID to continue, or
            None to start a new conversation.
        db: Active SQLAlchemy database session.

    Returns:
        dict: Normalized research result with conversation_id and
            turn_number added to the standard research result shape.

    Raises:
        ApplicationError: If the question fails validation.
    """
    try:
        user_query = validate_and_clean_question(question)
    except ValueError as exc:
        raise ApplicationError(str(exc)) from exc

    if conversation_id is None:
        conversation_id = str(uuid.uuid4())  # type: ignore[attr-defined]

    logger.info(
        "Chat turn started. conversation_id=%s turn question='%s'",
        conversation_id,
        user_query[:50],
    )

    conversation_history = get_conversation_history(
        db, conversation_id, MAX_HISTORY_TURNS
    )

    if conversation_history:
        history = conversation_history
    else:
        history = None

    if history is not None:
        turn_number = len(history) + 1
    else:
        turn_number = 1

    graph = build_graph()
    initial_state = _build_chat_initial_state(user_query, conversation_id, history)
    final_state = graph.invoke(initial_state)
    result = normalize_state(final_state, user_query)

    try:
        save_run(db, result, conversation_id, turn_number)
    except SQLAlchemyError:
        logger.exception("Failed to save chat run to database")

    result["conversation_id"] = conversation_id
    result["turn_number"] = turn_number

    logger.info(
        "Chat turn completed. conversation_id=%s turn=%d status=%s",
        conversation_id,
        turn_number,
        result.get("status"),
    )

    return result
