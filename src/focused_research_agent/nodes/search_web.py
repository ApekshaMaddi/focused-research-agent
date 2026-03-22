from focused_research_agent.services.search_factory import get_search_provider
from focused_research_agent.state import ResearchState


def search_web(state: ResearchState) -> dict:
    """Search the web using the generated queries.

    This node retrieves the active search provider from the factory,
    executes the queries, and stores normalized sources in state.

    Args:
        state: The current research state.

    Returns:
        dict: A partial state update containing sources and status,
        or an errors field if search fails.
    """
    queries = state.get("queries")

    if not isinstance(queries, list):
        return {"errors": ["search_web: queries must be a list"]}

    if not queries:
        return {"errors": ["search_web: No queries found"]}

    try:
        search_provider = get_search_provider()
        search_results = search_provider.search(queries)
    except Exception as e:
        return {"errors": [f"search_web failed: {e}"]}

    return {"sources": search_results, "status": "searched"}
