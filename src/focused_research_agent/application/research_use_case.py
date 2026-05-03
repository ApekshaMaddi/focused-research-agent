"""
Application-layer research use case for the Focused Research Agent.

This module contains the application-level logic for executing the research
use case. It sits between transport layers such as CLI, FastAPI, or
Streamlit and the underlying LangGraph workflow.

Architecturally, the application layer contains use-case/business logic.
It coordinates research execution while keeping terminal, HTTP, and other
transport concerns out of the core execution path.
"""

from focused_research_agent.application.exceptions import ApplicationError
from focused_research_agent.application.question_validation import (
    validate_and_clean_question,
)
from focused_research_agent.graph import build_graph
from focused_research_agent.state import ResearchState


def _is_list_of_strings(value: object) -> bool:
    """
    Check whether a value is a list containing only strings.

    Args:
        value: Value to validate.

    Returns:
        bool: True if the value is a list of strings, otherwise False.
    """
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_list_of_dicts(value: object) -> bool:
    """
    Check whether a value is a list containing only dictionaries.

    Args:
        value: Value to validate.

    Returns:
        bool: True if the value is a list of dictionaries, otherwise False.
    """
    return isinstance(value, list) and all(isinstance(item, dict) for item in value)


def normalize_state(final_state: ResearchState, user_query: str) -> dict:
    """
    Normalize raw graph state into a stable transport-facing result shape.

    This function ensures the application layer returns a predictable
    structure for both CLI and API consumers, even when the raw graph state
    is missing optional fields or contains malformed list values.

    Args:
        final_state: Final state returned by the LangGraph workflow.
        user_query: Cleaned user question used as a fallback value.

    Returns:
        dict: Normalized research result containing the fields expected by
            transport layers.
    """
    normalized_state = {
        "run_id": final_state.get("run_id") or "",
        "question": final_state.get("question") or user_query,
        "status": final_state.get("status") or "error",
        "scope": final_state.get("scope"),
        "queries": None,
        "sources": None,
        "answer": final_state.get("answer"),
        "citations": None,
        "errors": [],
    }

    queries = final_state.get("queries")
    if _is_list_of_strings(queries):
        normalized_state["queries"] = queries

    sources = final_state.get("sources")
    if _is_list_of_dicts(sources):
        normalized_state["sources"] = sources

    citations = final_state.get("citations")
    if _is_list_of_strings(citations):
        normalized_state["citations"] = citations

    errors = final_state.get("errors")
    if _is_list_of_strings(errors):
        normalized_state["errors"] = errors

    return normalized_state


def make_initial_state(question: str) -> ResearchState:
    """
    Create the starting graph state for a research run.

    Args:
        question: Cleaned user research question.

    Returns:
        ResearchState: Initial shared state expected by the LangGraph
            workflow.
    """
    initial_state: ResearchState = {
        "run_id": "",
        "question": question,
        "scope": None,
        "assumptions": None,
        "constraints": None,
        "queries": None,
        "sources": None,
        "answer": None,
        "citations": None,
        "status": "started",
        "errors": [],
        "debug": None,
        "conversation_id": None,
        "conversation_history": None,
    }

    return initial_state


def research_question(question: str) -> dict:
    """
    Execute the research use case for a user question.

    This function validates the incoming question, prepares the initial
    graph state, builds the LangGraph workflow, invokes it, and returns a
    normalized result to the calling transport layer.

    The shared question validator raises ValueError so it can be reused by
    Pydantic/FastAPI request validation. At the application-layer boundary,
    that ValueError is translated into ApplicationError so transport layers
    can handle expected use-case failures consistently.

    Args:
        question: User research question.

    Returns:
        dict: Normalized research result produced by the workflow.

    Raises:
        ApplicationError: If the question is invalid for the research use
            case.
    """
    try:
        user_query = validate_and_clean_question(question)
    except ValueError as exc:
        raise ApplicationError(str(exc)) from exc

    graph = build_graph()
    initial_state = make_initial_state(user_query)
    final_state = graph.invoke(initial_state)

    return normalize_state(final_state, user_query)
