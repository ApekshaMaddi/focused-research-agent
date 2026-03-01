from focused_research_agent.state import ResearchState

def mock_sources() -> list[dict]:
    return [
        {
            "title": "Overview: Topic background and key definitions",
            "url": "https://example.com/topic-overview",
            "snippet": "A high-level introduction covering the main concepts...",
            "source": "stub",
            "score": None,
        },
        {
            "title": "Key facts and practical details",
            "url": "https://example.com/topic-key-facts",
            "snippet": "A short list of important facts, common use cases...",
            "source": "stub",
            "score": None,
        },
        {
            "title": "Recent updates and current state of the topic",
            "url": "https://example.com/topic-recent-updates",
            "snippet": "A summary of recent developments and changes...",
            "source": "stub",
            "score": None,
        },
    ]

def search_web(state: ResearchState) -> dict:
    queries = state.get("queries") or []

    if not queries:
        return {"sources": [], "status": "searched"}

    return {"sources": mock_sources(), "status": "searched"}