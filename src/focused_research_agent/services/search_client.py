from tavily import TavilyClient
from focused_research_agent.config import get_search_config

def get_config():
    config = get_search_config()

    if (not "provider" in config) or (not "api_key" in config) or (not "max_results" in config):
        config =     {
        "provider": None,
        "api_key": None,
        "max_results": None,
    }


    return config

def call_search_client():
    search_client_config = get_config()

    # Step 1. Instantiating your TavilyClient
    tavily_client = TavilyClient(api_key=search_client_config.get("search_api_key"))

    # Step 2. Executing a simple search query
    response = tavily_client.search("Who is Leo Messi?")

    # Step 3. That's it! You've done a Tavily Search!
    print(response)

if __name__ == "__main__":
    get_config()
