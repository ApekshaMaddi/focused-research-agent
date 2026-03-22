# builds & compiles the StateGraph
from langgraph.graph import StateGraph, START, END
from focused_research_agent.state import ResearchState
from focused_research_agent.nodes.init_run import initialize_state
from focused_research_agent.nodes.scope_question import scope_question
from focused_research_agent.nodes.generate_queries import generate_queries
from focused_research_agent.nodes.search_web import search_web
from focused_research_agent.nodes.synthesize_answer import synthesize_answer
from focused_research_agent.nodes.finalize_run import finalize_run
from focused_research_agent.services.llm_factory import get_llm_provider
from focused_research_agent.nodes.handle_error import handle_error

def route_after_node(state: ResearchState) -> str:
    """
    After any node runs, check if errors were recorded.
    If yes, route to the error handler. Otherwise continue.
    """
    if state.get("errors"):
        return "handle_error"
    return "continue"

def build_graph():
    # Build providers ONCE here
    llm = get_llm_provider()

    # Wrap each node in a closure that captures the provider
    def _scope_question(state):
        return scope_question(state, llm)

    def _generate_queries(state):
        return generate_queries(state, llm)

    def _synthesize_answer(state):
        return synthesize_answer(state, llm)

    builder = StateGraph(ResearchState)
    builder.add_node("init_run", initialize_state)
    builder.add_node("scope_question", _scope_question)
    builder.add_node("generate_queries", _generate_queries)
    builder.add_node("search_web", search_web)
    builder.add_node("synthesize_answer", _synthesize_answer)
    builder.add_node("finalize_run", finalize_run)
    builder.add_node("handle_error", handle_error)

    builder.add_edge(START, "init_run")

    builder.add_conditional_edges(
        "init_run",
        route_after_node,
        {"continue": "scope_question", "handle_error": "handle_error"}
    )
    builder.add_conditional_edges(
        "scope_question",
        route_after_node,
        {"continue": "generate_queries", "handle_error": "handle_error"}
    )
    builder.add_conditional_edges(
        "generate_queries",
        route_after_node,
        {"continue": "search_web", "handle_error": "handle_error"}
    )
    builder.add_conditional_edges(
        "search_web",
        route_after_node,
        {"continue": "synthesize_answer", "handle_error": "handle_error"}
    )
    builder.add_conditional_edges(
        "synthesize_answer",
        route_after_node,
        {"continue": "finalize_run", "handle_error": "handle_error"}
    )

    builder.add_edge("finalize_run", END)
    builder.add_edge("handle_error", END)

    return builder.compile()


focused_research_agent_graph = build_graph()
