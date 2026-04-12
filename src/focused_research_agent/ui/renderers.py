"""Presentation helpers for the Streamlit UI.

This module contains only rendering code. It does not call the backend and it
does not contain business logic.
"""

from typing import Any

import streamlit as st


def render_page_header(api_base_url: str) -> None:
    """Render the page title and a short description.

    Args:
        api_base_url: Backend base URL shown for local debugging.
    """
    st.title("Focused Research Agent")
    st.caption("Thin Streamlit UI on top of the existing FastAPI backend.")
    st.caption(f"Backend API base URL: {api_base_url}")


def render_question_form(default_question: str) -> tuple[bool, str]:
    """Render the question form.

    Args:
        default_question: Question text to prefill in the form.

    Returns:
        A tuple containing the submit flag and the question text.
    """
    with st.form("research_form"):
        question = st.text_area(
            "Enter your research question",
            value=default_question,
            height=140,
        )
        submitted = st.form_submit_button("Run research")

    return submitted, question


def render_error_message(message: str) -> None:
    """Render a top-level UI error.

    Args:
        message: User-facing error text.
    """
    st.error(message)


def render_result(result: dict[str, Any]) -> None:
    """Render the normalized backend result.

    Args:
        result: Normalized result returned by the API client.
    """
    st.divider()
    st.subheader("Result")

    render_basic_fields(result)
    render_answer_section(result)
    render_sources_section(result)
    render_citations_section(result)
    render_workflow_errors_section(result)
    render_trace_section(result)


def render_basic_fields(result: dict[str, Any]) -> None:
    """Render the basic top fields.

    Args:
        result: Normalized result returned by the API client.
    """
    question = result.get("question", "")
    status = result.get("status", "")
    run_id = result.get("run_id", "")

    if question != "":
        st.write(f"**Question:** {question}")

    if status != "":
        st.write(f"**Status:** {status}")

    if run_id != "":
        st.caption(f"Run ID: {run_id}")


def render_answer_section(result: dict[str, Any]) -> None:
    """Render the final answer section.

    Args:
        result: Normalized result returned by the API client.
    """
    st.markdown("### Answer")

    answer = result.get("answer", "")
    if isinstance(answer, str):
        if answer.strip() != "":
            st.write(answer)
            return

    st.info("No answer was returned.")


def render_sources_section(result: dict[str, Any]) -> None:
    """Render the sources section.

    Args:
        result: Normalized result returned by the API client.
    """
    st.markdown("### Sources")

    sources = result.get("sources", [])
    if not isinstance(sources, list):
        st.caption("No sources returned.")
        return

    if len(sources) == 0:
        st.caption("No sources returned.")
        return

    index = 1
    for source in sources:
        render_single_source(index, source)
        index = index + 1


def render_single_source(index: int, source: Any) -> None:
    """Render one source item.

    Args:
        index: Display index.
        source: One source object.
    """
    if not isinstance(source, dict):
        st.write(f"{index}. {source}")
        return

    title = source.get("title", "")
    url = source.get("url", "")
    snippet = read_source_snippet(source)

    if title == "":
        title = f"Source {index}"

    if isinstance(url, str):
        if url.strip() != "":
            st.markdown(f"**{index}. [{title}]({url})**")
        else:
            st.markdown(f"**{index}. {title}**")
    else:
        st.markdown(f"**{index}. {title}**")

    if isinstance(snippet, str):
        if snippet.strip() != "":
            st.write(snippet)


def read_source_snippet(source: dict[str, Any]) -> Any:
    """Read the best available snippet field from one source.

    Args:
        source: Source dictionary.

    Returns:
        Source snippet text when present.
    """
    snippet = source.get("snippet")
    if snippet is not None:
        return snippet

    content = source.get("content")
    if content is not None:
        return content

    summary = source.get("summary")
    return summary


def render_citations_section(result: dict[str, Any]) -> None:
    """Render the citations section.

    Args:
        result: Normalized result returned by the API client.
    """
    st.markdown("### Citations")

    citations = result.get("citations", [])
    if not isinstance(citations, list):
        st.caption("No citations returned.")
        return

    if len(citations) == 0:
        st.caption("No citations returned.")
        return

    index = 1
    for citation in citations:
        if isinstance(citation, dict):
            st.write(f"{index}.")
            st.json(citation)
        else:
            st.write(f"{index}. {citation}")
        index = index + 1


def render_workflow_errors_section(result: dict[str, Any]) -> None:
    """Render workflow-level errors returned inside a normal result.

    Args:
        result: Normalized result returned by the API client.
    """
    errors = result.get("errors", [])
    if not isinstance(errors, list):
        return

    if len(errors) == 0:
        return

    st.markdown("### Workflow errors")

    for error in errors:
        st.warning(str(error))


def render_trace_section(result: dict[str, Any]) -> None:
    """Render scope and queries inside an expander.

    Args:
        result: Normalized result returned by the API client.
    """
    with st.expander("Research trace"):
        render_scope_section(result)
        render_queries_section(result)


def render_scope_section(result: dict[str, Any]) -> None:
    """Render the scope field.

    Args:
        result: Normalized result returned by the API client.
    """
    st.markdown("#### Scope")

    scope = result.get("scope")
    if scope is None:
        st.caption("No scope returned.")
        return

    if isinstance(scope, dict):
        st.json(scope)
        return

    if isinstance(scope, list):
        st.json(scope)
        return

    if isinstance(scope, str):
        if scope.strip() == "":
            st.caption("No scope returned.")
            return

    st.write(scope)


def render_queries_section(result: dict[str, Any]) -> None:
    """Render the generated query list.

    Args:
        result: Normalized result returned by the API client.
    """
    st.markdown("#### Generated queries")

    queries = result.get("queries", [])
    if not isinstance(queries, list):
        st.caption("No queries returned.")
        return

    if len(queries) == 0:
        st.caption("No queries returned.")
        return

    index = 1
    for query in queries:
        st.write(f"{index}. {query}")
        index = index + 1
