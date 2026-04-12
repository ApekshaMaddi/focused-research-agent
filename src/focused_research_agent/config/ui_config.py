"""Configuration helpers for the Streamlit UI.

This module keeps Streamlit configuration in one place so that the page file
and API client stay simple. The values are read from environment variables.
That means the code does not need to hardcode the API base URL, the research
path, or the timeout.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class UIConfigError(Exception):
    """Raised when the Streamlit UI configuration is missing or invalid."""


@dataclass(frozen=True)
class UISettings:
    """Settings used by the Streamlit UI.

    Attributes:
        api_base_url: Base URL of the FastAPI backend.
        research_path: Path of the research endpoint.
        timeout_seconds: Request timeout used by the UI HTTP client.
    """

    api_base_url: str
    research_path: str
    timeout_seconds: float


def load_ui_settings() -> UISettings:
    """Load Streamlit UI settings from environment variables.

    Returns:
        A populated UISettings object.

    Raises:
        UIConfigError: If any required environment variable is missing or if
            the timeout cannot be converted to a float.
    """
    load_dotenv()

    api_base_url = get_required_env("FOCUSED_RESEARCH_AGENT_BASE_URL")
    research_path = get_required_env("FOCUSED_RESEARCH_AGENT_RESEARCH_PATH")
    timeout_text = get_required_env("FOCUSED_RESEARCH_AGENT_TIMEOUT_SECONDS")
    timeout_seconds = parse_timeout_seconds(timeout_text)

    settings = UISettings(
        api_base_url=api_base_url,
        research_path=research_path,
        timeout_seconds=timeout_seconds,
    )
    return settings


def get_required_env(name: str) -> str:
    """Read one required environment variable.

    Args:
        name: Name of the environment variable.

    Returns:
        The non-empty environment variable value.

    Raises:
        UIConfigError: If the variable is missing or blank.
    """
    value = os.getenv(name)

    if value is None:
        raise UIConfigError(f"Missing required environment variable: {name}")

    if value.strip() == "":
        raise UIConfigError(f"Environment variable cannot be blank: {name}")

    return value


def parse_timeout_seconds(value: str) -> float:
    """Convert timeout text into a float.

    Args:
        value: Timeout text read from the environment.

    Returns:
        Timeout in seconds.

    Raises:
        UIConfigError: If the value is not a valid float.
    """
    try:
        timeout_seconds = float(value)
    except ValueError as exc:
        raise UIConfigError(
            "FOCUSED_RESEARCH_AGENT_API_TIMEOUT_SECONDS must be a number"
        ) from exc

    return timeout_seconds
