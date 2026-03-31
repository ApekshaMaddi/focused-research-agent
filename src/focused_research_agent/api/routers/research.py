from fastapi import APIRouter
from fastapi import status
from focused_research_agent.api.schemas.research import research as research_schema
from focused_research_agent.application import research_use_case


'''
Research API endpoints for the Focused Research Agent.

This module exposes HTTP endpoints related to the research use case. It
receives validated API input, forwards execution to the application layer,
and returns the application result as an HTTP response.

Architecturally, this module belongs to the transport layer. Routers are
transport adapters and should stay thin. They should not contain workflow
orchestration or provider-specific logic.
'''



research_router = APIRouter(
    tags=["research"]
)

@research_router.post("/research", status_code=status.HTTP_200_OK)
def research(search: research_schema.ResearchRequest)-> dict:
    """
    Handle a research request through the API.

    This endpoint accepts a validated research request, forwards the user
    question to the application layer, and returns the resulting response.

    At the current stage of the project, the application layer returns a
    placeholder response. Later, this endpoint will remain thin while the
    application layer invokes the LangGraph research workflow.

    Args:
    search: Validated research request payload.

    Returns:
    dict: Structured research response returned by the application layer.
    """
    search_result = research_use_case.research_runner(search.question)

    return search_result
