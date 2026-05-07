"""
Conversation history endpoints for the Focused Research Agent API.

This module exposes read-only HTTP endpoints for fetching conversation
history. It is used by the chat UI to populate the sidebar history
panel and to reload full conversations when selected.

Architecturally, this module belongs to the transport layer. It stays
thin — no business logic, no graph calls. It reads from the database
through the repository layer via dependency-injected sessions.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from focused_research_agent.database.database import get_db
from focused_research_agent.database.repository import (
    get_all_conversations,
    get_conversation_turns,
)

conversations_router = APIRouter(tags=["conversations"])


@conversations_router.get("/conversations", status_code=status.HTTP_200_OK)
def get_conversations(db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    """
    Return a summary list of all conversations.

    Returns one entry per conversation showing the conversation ID,
    title derived from the first question, and creation timestamp.
    Ordered newest first.

    Args:
        db: Injected SQLAlchemy database session.

    Returns:
        list[dict]: List of conversation summary dicts containing
            conversation_id, title, and created_at keys.
    """
    return get_all_conversations(db)


@conversations_router.get(
    "/conversations/{conversation_id}", status_code=status.HTTP_200_OK
)
def get_conversation(
    conversation_id: str, db: Annotated[Session, Depends(get_db)]
) -> list[dict]:
    """
    Return all turns of a specific conversation in chronological order.

    Returns complete research data for every turn including deserialized
    queries, sources, citations, and errors. Used to reload a full
    conversation into the chat UI.

    Args:
        conversation_id: UUID string identifying the conversation.
        db: Injected SQLAlchemy database session.

    Returns:
        list[dict]: List of complete turn dicts in chronological order.
            Empty list if the conversation does not exist.
    """
    return get_conversation_turns(db, conversation_id)


@conversations_router.get(
    "/reports",
    status_code=status.HTTP_200_OK,
)
def get_reports(db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    """
    Return a summary list of all report runs for the report history
    sidebar.

    Args:
        db: Injected SQLAlchemy database session.

    Returns:
        list[dict]: List of report summary dicts containing
            conversation_id, title, and created_at keys.
    """
    from focused_research_agent.database.repository import get_all_reports
    return get_all_reports(db)
