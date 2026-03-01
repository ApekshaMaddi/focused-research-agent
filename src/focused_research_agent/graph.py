# builds & compiles the StateGraph
from langgraph.graph import StateGraph, START, END
from focused_research_agent.state import ResearchState
from focused_research_agent.nodes.init_run import initialize_state
from focused_research_agent.nodes.scope_question import scope_question
from focused_research_agent.nodes.generate_queries import generate_queries
from focused_research_agent.nodes.search_web import search_web
from focused_research_agent.nodes.synthesize_answer import synthesize_answer
from focused_research_agent.nodes.finalize_run import finalize_run


def build_graph():

    builder = StateGraph(ResearchState)
    builder.add_node("init_run",initialize_state)
    builder.add_node("scope_question",scope_question)
    builder.add_node("generate_queries",generate_queries)
    builder.add_node("search_web",search_web)
    builder.add_node("synthesize_answer",synthesize_answer)
    builder.add_node("finalize_run",finalize_run)



    builder.add_edge(START,"init_run")
    builder.add_edge("init_run","scope_question")
    builder.add_edge("scope_question","generate_queries")
    builder.add_edge("generate_queries","search_web")
    builder.add_edge("search_web","synthesize_answer")
    builder.add_edge("synthesize_answer","finalize_run")
    builder.add_edge("finalize_run",END)

    return builder.compile()


focused_research_agent_graph = build_graph()