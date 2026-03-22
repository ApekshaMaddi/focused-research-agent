from focused_research_agent.graph import focused_research_agent_graph
from focused_research_agent.state import ResearchState
import focused_research_agent.services.llm_client as llm_client
import focused_research_agent.nodes.search_web as search_web_node


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


def fake_generate_json(prompt: str) -> dict:
    if (
        "The JSON MUST have exactly these keys:\n- answer (string)\n- citations (list of 1 to 5 URLs)"
        in prompt
    ):
        return {
            "answer": "The test topic can be understood by looking at its overview, rules, and common pitfalls.",
            "citations": [
                "https://example.com/overview",
                "https://example.com/rules",
                "https://example.com/pitfalls",
            ],
        }

    if 'Return EXACTLY one key: "queries".' in prompt:
        return {
            "queries": [
                "test topic overview",
                "test topic rules",
                "test topic examples",
                "test topic pitfalls",
            ]
        }

    return {
        "scope": "Explain the test topic clearly",
        "assumptions": ["User is a beginner", "General context"],
        "constraints": {
            "geography": "Global",
            "time_range": "current",
            "depth": "intro",
        },
    }


class FakeSearchProvider:
    def search(self, queries: list[str]) -> list[dict]:
        return [
            {
                "title": "Overview of the test topic",
                "url": "https://example.com/overview",
                "snippet": "A high-level overview of the test topic.",
                "source": "mock",
                "score": 0.95,
            },
            {
                "title": "Rules and requirements",
                "url": "https://example.com/rules",
                "snippet": "Important rules and requirements for the test topic.",
                "source": "mock",
                "score": 0.91,
            },
            {
                "title": "Common pitfalls and examples",
                "url": "https://example.com/pitfalls",
                "snippet": "Examples and common pitfalls for the test topic.",
                "source": "mock",
                "score": 0.89,
            },
        ]


def fake_get_search_provider():
    return FakeSearchProvider()


def test_graph_smoke_run(monkeypatch):
    monkeypatch.setattr(llm_client, "generate_json", fake_generate_json)
    monkeypatch.setattr(
        search_web_node, "get_search_provider", fake_get_search_provider
    )

    initial_state = make_initial_state("test question")
    final_state = focused_research_agent_graph.invoke(initial_state)

    assert final_state["run_id"]
    assert final_state["scope"]
    assert final_state["queries"]
    assert final_state["sources"]
    assert final_state["answer"]
    assert final_state["citations"]
    assert final_state["status"] == "completed"
