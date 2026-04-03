"""
Application-layer research use case for the Focused Research Agent.

This module contains the application-level logic for executing the research
use case. It sits between transport layers such as CLI, FastAPI, or
Streamlit and the underlying LangGraph workflow.

Architecturally, the application layer contains use-case/business logic.
It coordinates research execution while keeping terminal, HTTP, and other
transport concerns out of the core execution path.
"""

from focused_research_agent.state import ResearchState
from focused_research_agent.graph import build_graph


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
        "run_id": "",  # set by init_run node
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
    }

    return initial_state


def research_question(question: str) -> dict:
    """
    Execute the research use case for a user question.

    This function validates the incoming question, prepares the initial
    graph state, builds the LangGraph workflow, invokes it, and returns
    the final graph state to the calling transport layer.

    Args:
        question: User research question.

    Returns:
        dict: Final graph state produced by the research workflow.

    Raises:
        ValueError: If the question is not a string or is empty after
        trimming whitespace.
    """
    if not isinstance(question, str):
        raise ValueError("research_use_case: User query must be a string")

    user_query = question.strip()

    if not user_query:
        raise ValueError("research_use_case: No user query provided")

    graph = build_graph()
    initial_state = make_initial_state(user_query)
    final_state = graph.invoke(initial_state)

    return final_state