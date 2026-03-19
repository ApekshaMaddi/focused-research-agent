# CLI entrypoint (python -m focused_research_agent.cli)
from focused_research_agent.state import ResearchState
from focused_research_agent.graph import focused_research_agent_graph
from focused_research_agent.config.logger_config import setup_logging

import logging
logger = logging.getLogger("focused_research_agent.cli")


def make_initial_state(question:str) -> ResearchState:
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
    if not queries:
        return "(no queries)\n"

    lines = []
    for q in queries:
        lines.append("- " + q)

    return "\n".join(lines) + "\n"

def format_sources(sources: list[dict] | None) -> str:

    if not sources:
        return "(no sources)\n"

    else:
        result = []
        i=1
        for source in sources:
            title = source.get("title") or "No Title"
            url = source.get("url") or "No URL"
            line = f"{i}. {title} — {url}"
            result.append(line)
            i=i+1

        return "\n".join(result)

def format_citations(citations: list[str] | None):
    if not citations:
        return "(no citations)\n"

    lines = []
    for c in citations:
        lines.append("- " + c)

    return "\n".join(lines) + "\n"


def format_output(state: dict) -> str:
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


def format_error_output(message)-> str:

    return f"""
    ==============================
    STATUS: 
    Error
    
    ERROR: 
    {message}
    ==============================
    """.strip()


if __name__ == "__main__":
    setup_logging()
    user_question = input("What is your question? ").strip()
    if not user_question:
        print("Please enter a question.")
    else:

        initial_state = make_initial_state(user_question)

        try:
            final_state = focused_research_agent_graph.invoke(initial_state)
            print(format_output(final_state))
        except ValueError as e:
            print(format_error_output(e))
            logger.error(str(e))
        except Exception as e:
            print(format_error_output(f"Unexpected internal error occurred: {e}"))
            logger.error(str(e))



