import pytest

import focused_research_agent.application.research_use_case as use_case_module


class FakeGraph:
    def invoke(self, initial_state: dict) -> dict:
        return {
            "run_id": "run-456",
            "question": initial_state["question"],
            "status": "completed",
            "scope": "Explain the topic clearly",
            "queries": ["query one", "query two", "query three"],
            "sources": [
                {
                    "title": "Test Source",
                    "url": "https://example.com/source",
                    "snippet": "A test source snippet.",
                    "source": "mock",
                    "score": 0.9,
                }
            ],
            "answer": "This is a synthesized answer.",
            "citations": ["https://example.com/source"],
            "errors": [],
        }


def fake_build_graph():
    return FakeGraph()


def test_make_initial_state_returns_expected_shape():
    result = use_case_module.make_initial_state("test question")

    assert result["run_id"] == ""
    assert result["question"] == "test question"
    assert result["scope"] is None
    assert result["assumptions"] is None
    assert result["constraints"] is None
    assert result["queries"] is None
    assert result["sources"] is None
    assert result["answer"] is None
    assert result["citations"] is None
    assert result["status"] == "started"
    assert result["errors"] == []
    assert result["debug"] is None


def test_research_question_raises_when_question_is_not_string():
    with pytest.raises(ValueError, match="User query must be a string"):
        use_case_module.research_question(123)  # type: ignore[arg-type]


def test_research_question_raises_when_question_is_blank():
    with pytest.raises(ValueError, match="No user query provided"):
        use_case_module.research_question("   ")


def test_research_question_returns_normalized_graph_result(monkeypatch):
    monkeypatch.setattr(use_case_module, "build_graph", fake_build_graph)

    result = use_case_module.research_question("   test question   ")

    assert result["run_id"] == "run-456"
    assert result["question"] == "test question"
    assert result["status"] == "completed"
    assert result["scope"] == "Explain the topic clearly"
    assert result["queries"] == ["query one", "query two", "query three"]
    assert len(result["sources"]) == 1
    assert result["answer"] == "This is a synthesized answer."
    assert result["citations"] == ["https://example.com/source"]
    assert result["errors"] == []