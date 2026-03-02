from focused_research_agent.graph import focused_research_agent_graph
from focused_research_agent.state import ResearchState


def make_initial_state(question: str) -> ResearchState:
    return {
        "run_id": "",
        "question": question,
        "scope": None,
        "assumptions": None,
        "constraints": None,
        "queries": None,
        "sources": None,
        "answer": None,
        "citations": None,
        "status": "started",
        "errors": [],
        "debug": None,
    }


def test_graph_smoke_run():
    initial_state = make_initial_state("test question")
    final_state = focused_research_agent_graph.invoke(initial_state)

    assert final_state["run_id"]
    assert final_state["scope"]
    assert final_state["queries"]
    assert final_state["sources"]
    assert final_state["answer"]
    assert final_state["citations"]
    assert final_state["status"] in {"completed", "error"}