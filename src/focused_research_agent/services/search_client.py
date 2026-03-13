from tavily import TavilyClient
from focused_research_agent.config import get_search_config


def get_search_client():
    search_config = get_search_config()
    tavily_client = TavilyClient(api_key=search_config["api_key"])
    return tavily_client

def search(queries: list[str]) -> list[dict]:
    if len(queries) == 0:
        raise ValueError("search_client: No queries provided")


    search_client = get_search_client()
    search_config = get_search_config()

    final_search_results = []
    seen_urls = set()


    for each_query in queries:
        response = search_client.search(query=each_query,search_depth="basic",max_results=search_config["max_results"])

        if isinstance(response, dict) and ("results" in response) and isinstance(response["results"], list):
            response_results = response["results"]
            for each_result in response_results:
                if each_result["url"] in seen_urls:
                    continue
                else:
                 dict_mapping = dict()
                 dict_mapping["title"]   =  each_result["title"]
                 dict_mapping["url"]     =  each_result["url"]
                 dict_mapping["snippet"] =  each_result["content"]
                 dict_mapping["source"]  =  search_config["provider"]
                 dict_mapping["score"]   =  each_result["score"]
                 seen_urls.add(dict_mapping["url"])
                 final_search_results.append(dict_mapping)
        else:
            raise ValueError("search_client: Tavily response missing valid results: {}".format(each_query))
    return final_search_results