"""
Streamlit report page for the Focused Research Agent UI.

This module implements the deep research report generation interface.
It uses Streamlit's multi-page convention — placing it in the pages/
folder with a 3_ prefix makes it appear third in the sidebar navigation.

The report page uses advanced Tavily search depth and a structured
prompt that produces a markdown report with Introduction, Key Findings,
Analysis, and Conclusion sections. Report generation takes longer than
quick research — users are informed of this via a caption and spinner.

Architecturally, this module is a UI transport entrypoint alongside
Home.py and the other pages. It follows the same thin wiring pattern.
"""

import streamlit as st
from focused_research_agent.ui.api_client import call_report, check_health
from focused_research_agent.ui.exceptions import BackendUnavailableError
from focused_research_agent.ui.views import render_health_status


def _init_session_state() -> None:
    """
    Initialise session state keys for the report page.
    ...
    """
    if "report_result" not in st.session_state:
        st.session_state.report_result = None

    if "report_question" not in st.session_state:
        st.session_state.report_question = ""

    if "report_generating" not in st.session_state:
        st.session_state.report_generating = False


def _render_sidebar() -> None:
    """
    Render sidebar content for the report page.

    Displays the page title and API health status.

    Returns:
        None
    """
    st.sidebar.title("📄 Report")
    render_health_status(check_health())


def _render_report_input() -> str | None:
    question = st.text_area(
        "What would you like a full report on?",
        height=100,
        placeholder="e.g. The impact of quantum computing on Artificial Intelligence",
    )
    if st.button("📄 Generate Report"):
        return question
    return None


def _render_report_result() -> None:
    if st.session_state.report_result is None:
        return

    result = st.session_state.report_result
    data = result["data"]

    if data.get("status") == "error" or data.get("answer") is None:
        errors = data.get("errors") or ["An unknown error occurred."]
        st.error(f"Research failed: {errors[0]}")
        if st.checkbox("🛠️ Show raw response"):
            st.json(result)
        return

    if result["success"]:
        st.success("✅ Report complete!")
        st.divider()

        # Render the structured markdown report
        st.markdown(data["answer"])

        st.divider()

        # Metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            queries = data.get("queries") or []
            st.metric("📋 Queries", len(queries))
        with col2:
            sources = data.get("sources") or []
            st.metric("🔗 Sources", len(sources))
        with col3:
            citations = data.get("citations") or []
            st.metric("✅ Citations", len(citations))

        st.divider()

        # Sources
        if data.get("sources"):
            st.subheader("📚 Sources")
            for source in data["sources"]:
                with st.expander(source["title"]):
                    st.write(source["url"])
                    st.caption(source["snippet"])

        st.divider()

        # Debug panel
        if st.checkbox("🛠️ Show raw response"):
            st.json(result)
    else:
        st.error(result["error"] or "An error occurred.")


st.set_page_config(page_title="Research Report", layout="centered")
st.title("📄 Research Report")
st.caption("Deep research with structured analysis — takes longer than quick research.")

_init_session_state()
_render_sidebar()

question = _render_report_input()

if question is not None:
    try:
        with st.spinner("Generating report — this may take a minute..."):
            result = call_report(question)
        st.session_state.report_result = result
    except BackendUnavailableError as e:
        st.error(str(e))
        st.stop()

_render_report_result()
