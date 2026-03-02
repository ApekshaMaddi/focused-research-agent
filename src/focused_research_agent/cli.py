# CLI entrypoint (python -m focused_research_agent.cli)
from focused_research_agent.state import ResearchState
from focused_research_agent.graph import focused_research_agent_graph

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


if __name__ == "__main__":
    user_question = input("What is your question? ").strip()
    initial_state = make_initial_state(user_question)
    #
    final_state = focused_research_agent_graph.invoke(initial_state)
    print(format_output(final_state))

