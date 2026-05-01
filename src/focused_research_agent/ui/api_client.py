"""
HTTP client for the Focused Research Agent Streamlit UI.

This module is the only file in the UI layer that knows about httpx.
It calls the FastAPI backend and returns plain Python dicts to the caller.
It contains no Streamlit code.

Architecturally, this module is an external integration adapter for the UI
transport layer — the same role search_provider_tavily.py plays for the
search integration, but pointing at the internal FastAPI backend instead
of an external API.
"""

from typing import TypedDict
import httpx
from focused_research_agent.config.ui_config import get_ui_settings
from focused_research_agent.ui.exceptions import BackendUnavailableError


_HEALTH_ENDPOINT = "/health"
_RESEARCH_ENDPOINT = "/api/v1/research"


class ResearchCallResult(TypedDict):
    success: bool
    data: dict | None
    error: str | None


def check_health() -> bool:
    """
    Check whether the FastAPI backend is reachable.

    Makes a GET request to the /health endpoint with a short fixed timeout.
    A failed health check is not an error — it means the backend is offline.
    This function never raises; it always returns a bool.

    Returns:
        bool: True if the backend responded with HTTP 200, False otherwise.
    """
    settings = get_ui_settings()
    try:
        response = httpx.get(f"{settings.api_base_url}{_HEALTH_ENDPOINT}", timeout=5.0)
        return response.status_code == 200
    except httpx.ConnectError:
        return False


def call_research(question: str) -> ResearchCallResult:
    """
    Send a research question to the FastAPI backend and return the result.

    Makes a POST request to the versioned research endpoint with the user's
    question as the JSON body. Always returns a ResearchCallResult with three
    keys: success, data, and error. The shape is consistent across all
    response paths so that app.py and views.py never have to guess what
    they are receiving.

    Args:
        question: The user's research question to send to the backend.

    Returns:
        ResearchCallResult: A typed dict with the following keys:
            - success (bool): True if the backend returned HTTP 200,
                False for all other responses.
            - data (dict | None): The full research response from the
                backend when success is True, otherwise None.
            - error (str | None): A human-readable error message when
                success is False, otherwise None.

    Raises:
        BackendUnavailableError: If the backend cannot be reached at
            the configured UI_API_BASE_URL. Raised instead of returning
            an error dict because a completely unreachable backend is a
            different category of failure from a bad response — it means
            the user needs to start the backend before trying again.
    """
    settings = get_ui_settings()
    return_dict: ResearchCallResult = {"success": False, "data": None, "error": None}
    try:
        response = httpx.post(
            f"{settings.api_base_url}{_RESEARCH_ENDPOINT}",
            json={"question": question},
            timeout=settings.request_timeout,
        )
        if response.status_code == 200:
            return_dict["success"] = True
            return_dict["data"] = response.json()
            return_dict["error"] = None
            return return_dict
        elif response.status_code == 400:
            return_dict["success"] = False
            return_dict["data"] = None
            return_dict["error"] = response.json()["detail"]
            return return_dict
        elif response.status_code == 422:
            return_dict["success"] = False
            return_dict["data"] = None
            return_dict["error"] = "Invalid question submitted."
            return return_dict
        else:
            return_dict["success"] = False
            return_dict["data"] = None
            return_dict["error"] = f"Unexpected error: {response.status_code}"
    except httpx.ConnectError:
        raise BackendUnavailableError(
            f"Cannot connect to backend at {settings.api_base_url} — is FastAPI running?"
        )
    except httpx.TimeoutException:
        return_dict["success"] = False
        return_dict["data"] = None
        return_dict["error"] = "Request timed out — research is taking too long."
    return return_dict
