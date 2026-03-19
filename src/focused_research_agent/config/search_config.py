import os
from dotenv import load_dotenv

load_dotenv()

def get_search_config():
    search_provider = os.getenv("SEARCH_PROVIDER")
    search_api_key = os.getenv("SEARCH_API_KEY")
    search_max_results = os.getenv("SEARCH_MAX_RESULTS")

    if ((not search_provider or not search_provider.strip())
            or (not search_api_key or not search_api_key.strip())
            or ( not search_max_results or not search_max_results.strip())):
        raise ValueError("Search provider, search provider api key and max results should be given in .env file!")

    try:
        search_max_results = int(search_max_results)
    except ValueError:
        raise ValueError(f"SEARCH_MAX_RESULTS must be an int. Got: {search_max_results}")

    if search_max_results<=0:
        raise ValueError("SEARCH_MAX_RESULTS must be a positive integer!")

    if search_provider != "tavily":
        raise ValueError("Provider must be 'tavily'")

    return {
        "provider": search_provider,
        "api_key": search_api_key,
        "max_results": search_max_results,
    }