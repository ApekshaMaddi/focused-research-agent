"""Small helpers for Streamlit session state.

This module keeps UI-only state in one place so the main page file stays short
and easy to explain.
"""

from typing import Any

import streamlit as st


LAST_QUESTION_KEY = "last_question"
LATEST_RESULT_KEY = "latest_result"
LATEST_ERROR_KEY = "latest_error"


def initialize_session_state() -> None:
    """Create the session-state keys used by the page.

    The function is safe to call on every rerun because it only creates keys
    that are missing.
    """
    if LAST_QUESTION_KEY not in st.session_state:
        st.session_state[LAST_QUESTION_KEY] = ""

    if LATEST_RESULT_KEY not in st.session_state:
        st.session_state[LATEST_RESULT_KEY] = None

    if LATEST_ERROR_KEY not in st.session_state:
        st.session_state[LATEST_ERROR_KEY] = None


def save_result(question: str, result: dict[str, Any]) -> None:
    """Save the latest successful result.

    Args:
        question: The submitted question.
        result: The normalized backend result.
    """
    st.session_state[LAST_QUESTION_KEY] = question
    st.session_state[LATEST_RESULT_KEY] = result
    st.session_state[LATEST_ERROR_KEY] = None


def save_error(question: str, message: str) -> None:
    """Save the latest UI error message.

    Args:
        question: The submitted question.
        message: The user-facing error message.
    """
    st.session_state[LAST_QUESTION_KEY] = question
    st.session_state[LATEST_RESULT_KEY] = None
    st.session_state[LATEST_ERROR_KEY] = message


def get_last_question() -> str:
    """Return the last submitted question.

    Returns:
        The last submitted question, or an empty string.
    """
    value = st.session_state.get(LAST_QUESTION_KEY, "")

    if isinstance(value, str):
        return value

    return ""


def get_latest_result() -> dict[str, Any] | None:
    """Return the latest successful result.

    Returns:
        The latest result dictionary, or None.
    """
    value = st.session_state.get(LATEST_RESULT_KEY)

    if isinstance(value, dict):
        return value

    return None


def get_latest_error() -> str | None:
    """Return the latest saved error message.

    Returns:
        The latest error string, or None.
    """
    value = st.session_state.get(LATEST_ERROR_KEY)

    if isinstance(value, str):
        if value != "":
            return value

    return None
