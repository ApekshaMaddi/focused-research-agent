# CLI entrypoint (python -m focused_research_agent.cli)
from focused_research_agent.state import ResearchState
from focused_research_agent.graph import build_graph
from focused_research_agent.config.logger_config import setup_logging

import logging
import sys

logger = logging.getLogger("focused_research_agent.cli")

EXIT_COMMANDS = {"exit", "quit", "bye"}

def make_initial_state(question: str) -> ResearchState:
    """
    Create the starting state for the research agent run.
    """

    initial_state: ResearchState = {
        "run_id": "",  # set by init_run node
        "question": question,  # user input
        # Scoping
        "scope": None,
        "assumptions": None,
        "constraints": None,
        # Planning
        "queries": None,
        # Search results
        "sources": None,
        # Synthesis
        "answer": None,
        "citations": None,
        # Operational
        "status": "started",
        "errors": [],
        "debug": None,
    }

    return initial_state


def format_queries(queries: list[str] | None) -> str:
    """Format generated queries for CLI display."""
    if not queries:
        return "(no queries)\n"

    lines = []
    for q in queries:
        lines.append("- " + q)

    return "\n".join(lines) + "\n"


def format_sources(sources: list[dict] | None) -> str:
    """Format collected sources for CLI display."""
    if not sources:
        return "(no sources)\n"

    else:
        result = []
        for i, source in enumerate(sources, start=1):
            title = source.get("title") or "No Title"
            url = source.get("url") or "No URL"
            result.append(f"{i}. {title} — {url}")
        return "\n".join(result)


def format_citations(citations: list[str] | None):
    """Format collected sources for CLI display."""
    if not citations:
        return "(no citations)\n"

    lines = []
    for c in citations:
        lines.append("- " + c)

    return "\n".join(lines) + "\n"


def format_output(state: dict) -> str:
    """Build the final CLI output block from graph state."""
    return f"""
==============================
QUESTION:
{state.get("question")}

RUN ID:
{state.get("run_id")}

STATUS:
{state.get("status")}

SCOPE:
{state.get("scope")}

QUERIES:
{format_queries(state.get("queries"))}
SOURCES (title + url):
{format_sources(state.get("sources"))}

ANSWER:
{state.get("answer")}

CITATIONS:
{format_citations(state.get("citations"))}
==============================
""".strip()


def format_error_output(message: str) -> str:
    """Build the CLI error output block."""

    return f"""
    ==============================
    STATUS: 
    Error
    
    ERROR: 
    {message}
    ==============================
    """.strip()



def get_user_question() -> str | None:
    user_question = " ".join(sys.argv[1:]).strip()

    if user_question:
        if user_question.lower() in EXIT_COMMANDS:
            return None
        else:
            return user_question

    while True:
        typed_question = input("What is your question? ").strip()

        if not typed_question:
            print("Please enter a question.")
            continue

        if typed_question.lower() in EXIT_COMMANDS:
            return None

        return typed_question


def main() -> None:
    setup_logging()

    user_question = get_user_question()
    graph = build_graph()
    initial_state = make_initial_state(user_question)

    try:
        final_state = graph.invoke(initial_state)
        print(format_output(final_state))
    except ValueError as e:
        print(format_error_output(str(e)))
        logger.error(str(e))
    except Exception as e:
        print(format_error_output(f"Unexpected internal error occurred: {e}"))
        logger.error(str(e))


if __name__ == "__main__":
    main()