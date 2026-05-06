"""
FastAPI dependency providers for the Focused Research Agent API.

This module contains dependency functions used by API routers to obtain
application-layer use cases and other injectable components.

Architecturally, this module belongs to the API layer. It helps keep routers
thin by separating dependency wiring from endpoint definitions.
"""

from collections.abc import Callable
from focused_research_agent.application import chat_use_case, report_use_case
from focused_research_agent.application import research_use_case


def get_research_use_case() -> Callable[[str], dict]:
    """
    Provide the application-layer research use case to API routes.

    This dependency returns the callable responsible for executing the
    research use case. The router can use the returned callable without
    directly importing the concrete implementation.

    Returns:
        Callable[[str], dict]: A callable that accepts a user question
        and returns a structured research result.
    """
    return research_use_case.research_question


def get_chat_use_case() -> Callable:
    """
    Provide the application-layer chat use case to API routes.

    Returns:
        Callable: A callable that accepts db, conversation_id, and
            question and returns a structured chat result.
    """
    return chat_use_case.execute_chat_turn


def get_report_use_case() -> Callable:
    """
    Provide the application-layer report use case to API routes.

    Returns:
        Callable: A callable that accepts question and db and returns
            a structured report result.
    """
    return report_use_case.execute_report
