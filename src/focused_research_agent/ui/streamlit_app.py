"""Thin Streamlit entry page for the Focused Research Agent.

This page stays intentionally small. It only does five things:

1. Load Streamlit UI settings.
2. Create the API client.
3. Show the question form.
4. Call the backend.
5. Render the saved result or error.

This keeps Streamlit as a presentation layer and leaves the real research logic
inside the existing FastAPI backend and application layer.
"""

import streamlit as st

from focused_research_agent.ui.api_client import (
    ApiBadRequestError,
    ApiClientError,
    ApiConnectionError,
    ApiServerError,
    ApiTimeoutError,
    ApiValidationError,
    ResearchApiClient,
)
from focused_research_agent.ui.renderers import (
    render_error_message,
    render_page_header,
    render_question_form,
    render_result,
)
from focused_research_agent.ui.session_state import (
    get_last_question,
    get_latest_error,
    get_latest_result,
    initialize_session_state,
    save_error,
    save_result,
)
from focused_research_agent.config.ui_config import UIConfigError, load_ui_settings


def main() -> None:
    """Run the Streamlit page."""
    st.set_page_config(
        page_title="Focused Research Agent",
        page_icon="🔎",
        layout="wide",
    )

    initialize_session_state()

    try:
        settings = load_ui_settings()
    except UIConfigError as exc:
        render_error_message(str(exc))
        return

    api_client = ResearchApiClient(settings)

    render_page_header(settings.api_base_url)

    default_question = get_last_question()
    submitted, question = render_question_form(default_question)

    if submitted:
        handle_submission(question, api_client)

    render_saved_output()


def handle_submission(question: str, api_client: ResearchApiClient) -> None:
    """Send the question to the backend and save the result or error.

    Args:
        question: Raw question typed by the user.
        api_client: Tiny HTTP client used by the Streamlit page.
    """
    try:
        with st.spinner("Researching your question..."):
            result = api_client.submit_question(question)
    except ApiValidationError as exc:
        save_error(question, f"Validation error: {exc}")
    except ApiBadRequestError as exc:
        save_error(question, f"Bad request: {exc}")
    except ApiServerError as exc:
        save_error(question, f"Server error: {exc}")
    except ApiTimeoutError as exc:
        save_error(question, f"Timeout error: {exc}")
    except ApiConnectionError as exc:
        save_error(question, f"Connection error: {exc}")
    except ApiClientError as exc:
        save_error(question, f"Unexpected API error: {exc}")
    else:
        save_result(question, result)


def render_saved_output() -> None:
    """Render the latest saved error or result."""
    latest_error = get_latest_error()
    if latest_error is not None:
        render_error_message(latest_error)

    latest_result = get_latest_result()
    if latest_result is not None:
        render_result(latest_result)


if __name__ == "__main__":
    main()
