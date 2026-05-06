"""
Chat API endpoint for the Focused Research Agent.

This module exposes the HTTP endpoint for conversation-aware research.
It receives a validated chat request, obtains a database session and
executes the chat use case through dependency injection, and returns
the structured chat response.

Architecturally, this module belongs to the transport layer. It stays
thin — no business logic, no database queries, no graph calls. It
delegates everything to the application layer through
execute_chat_turn.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from focused_research_agent.api.schemas.chat.chat import ChatRequest, ChatResponse
from focused_research_agent.database.database import get_db
from focused_research_agent.api.dependencies import get_chat_use_case
from collections.abc import Callable

chat_router = APIRouter(tags=["chat"])


@chat_router.post("/chat", status_code=status.HTTP_200_OK, response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Annotated[Session, Depends(get_db)],
    run_chat_use_case: Annotated[Callable, Depends(get_chat_use_case)],
) -> dict:
    """
    Handle a chat research request through the API.

    Accepts a validated chat request containing a question and optional
    conversation ID, executes the conversation-aware research use case,
    and returns the structured result with conversation metadata.

    Args:
        request: Validated chat request payload.
        db: Injected SQLAlchemy database session.

    Returns:
        dict: Structured chat response returned by the application layer.
    """
    return run_chat_use_case(
        db=db,
        conversation_id=request.conversation_id,
        question=request.question,
    )
