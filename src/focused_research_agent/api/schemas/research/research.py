from pydantic import BaseModel, StringConstraints
from typing import Annotated


"""
Pydantic request and response schemas for the research API.

This module defines the API contract for the research endpoint. These schemas
describe the request body accepted by the FastAPI route and the structured
response returned to API clients.

These models belong to the API boundary and should represent transport-level
data shapes, not internal graph state or provider-specific models.
"""

class ResearchRequest(BaseModel):
    """
    Request schema for submitting a research question through the API.

    This model represents the client payload required to trigger the research
    use case. At the current stage, it contains only the user’s question to keep
    the API contract minimal and focused.

    Attributes:
    question: The user’s research question.
    """
    question: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, strict=True),
    ]

class SourceResponse(BaseModel):
    """
    Schema representing one source returned in the research response.

    This model defines the transport-level shape of a normalized source item
    included in the API response.

    Attributes:
        title: Human-readable title of the source.
        url: Source URL.
        snippet: Short excerpt or summary from the source.
        source: Name of the originating source provider.
        score: Relevance score assigned during search.
    """
    title: str
    url: str
    snippet: str
    source: str
    score: float

class ResearchResponse(BaseModel):
    """
    Response schema returned by the research API endpoint.

    This model represents the structured API response for the research use case.
    It mirrors the main graph output fields exposed through the application layer
    and provides a stable transport-level response shape for clients.

    Attributes:
        run_id: Unique identifier for the research run.
        question: Original user question.
        status: Final status of the research run.
        scope: Scoped interpretation of the user's question.
        queries: Generated web-search queries.
        sources: Normalized source entries used in synthesis.
        answer: Final synthesized answer.
        citations: Citation URLs supporting the answer.
        errors: Collected workflow errors, if any.
    """

    run_id: str
    question: str
    status: str
    scope: str | None
    queries: list[str] | None
    sources: list[SourceResponse] | None
    answer: str | None
    citations: list[str] | None
    errors: list[str] | None