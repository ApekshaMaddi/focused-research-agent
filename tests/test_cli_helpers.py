import focused_research_agent.cli as cli_module

"""
What are we testing?
This file tests the pure helper functions in cli.py that format data for terminal output. These helpers do not call the graph, LLM, or search provider. They only convert already-available state into user-friendly text. The tests cover:

initial state creation
formatting queries
formatting sources
formatting citations
formatting the full success output
formatting the error output

How are we testing?
We call each helper function directly with simple test data and compare the returned string to the expected output. For example:

format_queries(None) should return the placeholder text for missing queries
format_queries([...]) should return a bullet list
format_sources([...]) should return a numbered list with title and URL
format_output(state) should include all major sections such as QUESTION, STATUS, ANSWER, and CITATIONS

Why is this useful?
These tests verify that the CLI presentation layer is predictable and stable. Even if the graph logic is correct, poor formatting can make the tool hard to use. 
Since these helpers are pure functions, they are ideal for fast, deterministic unit tests.

“This file tests only presentation logic. I separated output formatting from business logic, so I can test the CLI display independently from the graph and providers.”
"""


def test_make_initial_state_returns_expected_shape():
    result = cli_module.make_initial_state("test question")

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


def test_format_queries_returns_placeholder_when_none():
    result = cli_module.format_queries(None)

    assert result == "(no queries)\n"


def test_format_queries_formats_bullet_list():
    result = cli_module.format_queries(["query one", "query two"])

    assert result == "- query one\n- query two\n"


def test_format_sources_returns_placeholder_when_none():
    result = cli_module.format_sources(None)

    assert result == "(no sources)\n"


def test_format_sources_formats_numbered_list():
    sources = [
        {
            "title": "First Source",
            "url": "https://example.com/one",
        },
        {
            "title": "Second Source",
            "url": "https://example.com/two",
        },
    ]

    result = cli_module.format_sources(sources)

    assert result == (
        "1. First Source — https://example.com/one\n"
        "2. Second Source — https://example.com/two"
    )


def test_format_citations_returns_placeholder_when_none():
    result = cli_module.format_citations(None)

    assert result == "(no citations)\n"


def test_format_citations_formats_bullet_list():
    result = cli_module.format_citations(
        ["https://example.com/one", "https://example.com/two"]
    )

    assert result == "- https://example.com/one\n- https://example.com/two\n"


def test_format_output_contains_expected_sections():
    state = {
        "question": "test question",
        "run_id": "run-123",
        "status": "completed",
        "scope": "Explain the test topic",
        "queries": ["query one", "query two"],
        "sources": [
            {
                "title": "First Source",
                "url": "https://example.com/one",
            }
        ],
        "answer": "This is the answer.",
        "citations": ["https://example.com/one"],
    }

    result = cli_module.format_output(state)

    assert "QUESTION:" in result
    assert "RUN ID:" in result
    assert "STATUS:" in result
    assert "SCOPE:" in result
    assert "QUERIES:" in result
    assert "SOURCES (title + url):" in result
    assert "ANSWER:" in result
    assert "CITATIONS:" in result
    assert "test question" in result
    assert "run-123" in result
    assert "completed" in result
    assert "Explain the test topic" in result
    assert "- query one" in result
    assert "1. First Source — https://example.com/one" in result
    assert "This is the answer." in result
    assert "- https://example.com/one" in result


def test_format_error_output_contains_error_message():
    result = cli_module.format_error_output("Something failed")

    assert "STATUS:" in result
    assert "Error" in result
    assert "ERROR:" in result
    assert "Something failed" in result
