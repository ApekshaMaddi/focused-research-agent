from pydantic import BaseModel


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
    question: str


class ResearchResponse(BaseModel):
    """
    Response schema returned by the research API endpoint.

    This model represents the structured API response for the research use case.
    At the current stage, it is a placeholder response used to validate the API
    contract and route wiring before real graph execution is connected.

    Attributes:
    status: High-level status of the research request.
    question: The original question received by the API.
    message: Placeholder response message from the application layer.
    """
    status:str
    question:str
    message:str