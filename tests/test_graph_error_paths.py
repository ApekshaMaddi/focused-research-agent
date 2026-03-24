
import importlib
"""
Focused graph-level tests for error routing behavior.

What is tested:
- the graph routes to the error handler when the initial question is empty

How it is tested:
- patch the LLM factory with a fake provider
- reload graph.py so the compiled graph captures patched dependencies
- invoke the graph and assert final error status and message

Why it matters:
- verifies the Option B state-based error routing design
- proves that graph routing changes correctly when errors are present
"""
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


class FakeLLMProvider:
    def generate_json(self, prompt: str) -> dict:
        return {
            "scope": "Should never be used in empty-question test",
            "assumptions": ["placeholder", "placeholder"],
            "constraints": {},
        }


def fake_get_llm_provider():
    return FakeLLMProvider()


def test_graph_empty_question_routes_to_handle_error(monkeypatch):
    import focused_research_agent.services.llm_factory as llm_factory
    import focused_research_agent.graph as graph_module

    monkeypatch.setattr(llm_factory, "get_llm_provider", fake_get_llm_provider)

    graph_module = importlib.reload(graph_module)

    initial_state = make_initial_state("")
    final_state = graph_module.focused_research_agent_graph.invoke(initial_state)

    assert final_state["run_id"]
    assert final_state["status"] == "error"
    assert final_state["errors"] == ["init_run: No question provided"]
