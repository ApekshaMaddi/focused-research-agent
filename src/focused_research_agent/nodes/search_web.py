from focused_research_agent.interfaces.search_interface import SearchProvider
from focused_research_agent.state import ResearchState

_NUMBER_OF_IMAGES = 12
def search_web(state: ResearchState, search_provider: SearchProvider) -> dict:
    """Search the web using the generated queries.

    This node retrieves the active search provider from the factory,
    executes the queries, and stores normalized sources in state.

    Args:
        state: The current research state.
        search_provider: The active search provider instance.

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
        search_results, images = search_provider.search(queries)
    except Exception as e:
        return {"errors": [f"search_web failed: {e}"]}

    return {
        "sources": search_results,
        "images": images[:_NUMBER_OF_IMAGES],
        "status": "searched",
    }
