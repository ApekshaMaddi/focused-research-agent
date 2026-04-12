"""Very small HTTP client for the Streamlit UI.

This module hides raw HTTP details from the Streamlit page. The page should not
need to know how to build the URL, send the POST request, read JSON, or turn
HTTP status codes into user-friendly errors.
"""

from typing import Any

import requests

from focused_research_agent.config.ui_config import UISettings


class ApiClientError(Exception):
    """Base exception for UI-side API client failures."""


class ApiBadRequestError(ApiClientError):
    """Raised when the backend returns HTTP 400."""


class ApiValidationError(ApiClientError):
    """Raised when the backend returns HTTP 422."""


class ApiServerError(ApiClientError):
    """Raised when the backend returns HTTP 500 or another 5xx error."""


class ApiTimeoutError(ApiClientError):
    """Raised when the request times out."""


class ApiConnectionError(ApiClientError):
    """Raised when the UI cannot connect to the backend."""


class ApiResponseFormatError(ApiClientError):
    """Raised when the backend response format is not usable."""


class ResearchApiClient:
    """Tiny client that calls the research API.

    Args:
        settings: UI settings that contain the base URL, endpoint path,
            and timeout.
    """

    def __init__(self, settings: UISettings) -> None:
        """Store the settings used for API calls.

        Args:
            settings: UI settings for the backend connection.
        """
        self.settings = settings

    def submit_question(self, question: str) -> dict[str, Any]:
        """Send the question to the research endpoint.

        Args:
            question: User question collected by Streamlit.

        Returns:
            A normalized result dictionary for the render layer.

        Raises:
            ApiBadRequestError: If the backend returns HTTP 400.
            ApiValidationError: If the backend returns HTTP 422.
            ApiServerError: If the backend returns HTTP 5xx.
            ApiTimeoutError: If the request times out.
            ApiConnectionError: If the backend cannot be reached.
            ApiResponseFormatError: If the response JSON is invalid.
            ApiClientError: For other request problems.
        """
        endpoint = build_url(
            self.settings.api_base_url,
            self.settings.research_path,
        )
        payload = {"question": question}

        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=self.settings.timeout_seconds,
            )
        except requests.Timeout as exc:
            raise ApiTimeoutError("The request timed out.") from exc
        except requests.ConnectionError as exc:
            raise ApiConnectionError("Could not connect to the FastAPI backend.") from exc
        except requests.RequestException as exc:
            raise ApiClientError(f"HTTP request failed: {exc}") from exc

        raise_for_error_status(response)

        body = parse_json_body(response)
        if not isinstance(body, dict):
            raise ApiResponseFormatError("The backend returned JSON, but not a JSON object.")

        normalized_body = normalize_result_payload(body)
        return normalized_body


def build_url(base_url: str, path: str) -> str:
    """Join the base URL and endpoint path.

    Args:
        base_url: Backend base URL.
        path: Endpoint path.

    Returns:
        A full request URL.
    """
    cleaned_base_url = base_url
    cleaned_path = path

    if cleaned_base_url.endswith("/"):
        cleaned_base_url = cleaned_base_url[:-1]

    if not cleaned_path.startswith("/"):
        cleaned_path = "/" + cleaned_path

    full_url = cleaned_base_url + cleaned_path
    return full_url


def raise_for_error_status(response: requests.Response) -> None:
    """Turn failed HTTP responses into simple custom exceptions.

    Args:
        response: Raw HTTP response object.

    Raises:
        ApiBadRequestError: If the backend returns HTTP 400.
        ApiValidationError: If the backend returns HTTP 422.
        ApiServerError: If the backend returns HTTP 5xx.
        ApiClientError: For any other failed status.
    """
    status_code = response.status_code

    if status_code < 400:
        return

    error_message = extract_error_message(response)

    if status_code == 400:
        raise ApiBadRequestError(error_message)

    if status_code == 422:
        raise ApiValidationError(error_message)

    if status_code >= 500:
        raise ApiServerError(error_message)

    raise ApiClientError(f"API request failed with status {status_code}: {error_message}")


def parse_json_body(response: requests.Response) -> Any:
    """Parse the JSON body from a successful response.

    Args:
        response: Raw HTTP response object.

    Returns:
        Parsed JSON content.

    Raises:
        ApiResponseFormatError: If the body is not valid JSON.
    """
    try:
        body = response.json()
    except ValueError as exc:
        raise ApiResponseFormatError("The backend response was not valid JSON.") from exc

    return body


def normalize_result_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize the backend result so the UI can render safely.

    Args:
        payload: JSON object returned by the backend.

    Returns:
        A dictionary with stable keys and safe default values.
    """
    normalized_payload: dict[str, Any] = {}

    normalized_payload["run_id"] = payload.get("run_id", "")
    normalized_payload["question"] = payload.get("question", "")
    normalized_payload["status"] = payload.get("status", "")
    normalized_payload["scope"] = payload.get("scope")
    normalized_payload["answer"] = payload.get("answer", "")

    queries = payload.get("queries")
    if queries is None:
        queries = []
    normalized_payload["queries"] = queries

    sources = payload.get("sources")
    if sources is None:
        sources = []
    normalized_payload["sources"] = sources

    citations = payload.get("citations")
    if citations is None:
        citations = []
    normalized_payload["citations"] = citations

    errors = payload.get("errors")
    if errors is None:
        errors = []
    normalized_payload["errors"] = errors

    return normalized_payload


def extract_error_message(response: requests.Response) -> str:
    """Extract one readable error message from a failed response.

    This function is intentionally simple and delegates most work to smaller
    helper functions so the logic stays easy to understand and passes Sonar's
    cognitive complexity rule.

    Args:
        response: Failed HTTP response.

    Returns:
        A user-friendly error message.
    """
    payload = read_json_payload(response)

    if payload is None:
        return read_text_message(response)

    if not isinstance(payload, dict):
        return default_http_message(response)

    message = read_message_from_detail(payload)
    if message is not None:
        return message

    message = read_top_level_message(payload)
    if message is not None:
        return message

    message = read_errors_list_message(payload)
    if message is not None:
        return message

    return default_http_message(response)


def read_json_payload(response: requests.Response) -> Any | None:
    """Try to parse JSON from a failed response.

    Args:
        response: Failed HTTP response.

    Returns:
        Parsed JSON, or None when parsing fails.
    """
    try:
        payload = response.json()
    except ValueError:
        return None

    return payload


def read_text_message(response: requests.Response) -> str:
    """Read a fallback error message from the raw response text.

    Args:
        response: Failed HTTP response.

    Returns:
        Raw text when present, otherwise a default HTTP message.
    """
    text = response.text.strip()

    if text != "":
        return text

    return default_http_message(response)


def read_message_from_detail(payload: dict[str, Any]) -> str | None:
    """Read an error message from the 'detail' field.

    Args:
        payload: Failed response payload.

    Returns:
        A readable message, or None if no usable detail exists.
    """
    detail = payload.get("detail")

    if isinstance(detail, str):
        if detail.strip() != "":
            return detail
        return None

    if isinstance(detail, list):
        return join_validation_details(detail)

    if isinstance(detail, dict):
        return read_message_from_detail_dict(detail)

    return None


def join_validation_details(details: list[Any]) -> str | None:
    """Join validation detail items into one message.

    Args:
        details: Validation detail items.

    Returns:
        A combined string, or None if the list is empty.
    """
    if len(details) == 0:
        return None

    messages: list[str] = []

    for item in details:
        message = format_validation_detail(item)
        messages.append(message)

    combined_message = "; ".join(messages)
    return combined_message


def read_message_from_detail_dict(detail: dict[str, Any]) -> str | None:
    """Read an error message from a dictionary stored in 'detail'.

    Args:
        detail: Dictionary found inside the detail field.

    Returns:
        A message string, or None if not found.
    """
    message = detail.get("message")
    if isinstance(message, str):
        if message.strip() != "":
            return message

    error = detail.get("error")
    if isinstance(error, str):
        if error.strip() != "":
            return error

    return None


def read_top_level_message(payload: dict[str, Any]) -> str | None:
    """Read an error message from top-level message fields.

    Args:
        payload: Failed response payload.

    Returns:
        A message string, or None if not found.
    """
    message = payload.get("message")
    if isinstance(message, str):
        if message.strip() != "":
            return message

    error = payload.get("error")
    if isinstance(error, str):
        if error.strip() != "":
            return error

    return None


def read_errors_list_message(payload: dict[str, Any]) -> str | None:
    """Read a message from the top-level errors list.

    Args:
        payload: Failed response payload.

    Returns:
        A combined string, or None if no usable errors are present.
    """
    errors = payload.get("errors")

    if not isinstance(errors, list):
        return None

    if len(errors) == 0:
        return None

    messages: list[str] = []

    for item in errors:
        messages.append(str(item))

    combined_message = "; ".join(messages)
    return combined_message


def format_validation_detail(detail: Any) -> str:
    """Convert one validation detail item into readable text.

    Args:
        detail: One FastAPI or Pydantic validation detail item.

    Returns:
        A readable validation message.
    """
    if not isinstance(detail, dict):
        return str(detail)

    message = detail.get("msg", "Validation error")
    message_text = str(message)

    location = detail.get("loc")
    if isinstance(location, list) or isinstance(location, tuple):
        if len(location) > 0:
            location_parts: list[str] = []

            for item in location:
                location_parts.append(str(item))

            location_text = " -> ".join(location_parts)
            return f"{location_text}: {message_text}"

    return message_text


def default_http_message(response: requests.Response) -> str:
    """Build a simple fallback message from the HTTP status code.

    Args:
        response: Failed HTTP response.

    Returns:
        A fallback message.
    """
    return f"HTTP {response.status_code}"
