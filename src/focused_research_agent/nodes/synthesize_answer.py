from focused_research_agent.state import ResearchState

def synthesize_answer(state: ResearchState) -> dict:
    question = (state.get("question") or "").strip()
    sources = state.get("sources")

    if not question:
        raise ValueError("synthesize_answer:No question found")

    if not isinstance(sources, list) or (not sources):
        raise ValueError("synthesize_answer:No sources found")

    for item in sources:
            if not isinstance(item, dict):
                raise ValueError("synthesize_answer:Invalid item found")

    citations = list()
    citations_seen = set()
    titles = list()
    titles_seen = set()

    for source in sources:
        url = source.get("url")
        if url and url not in citations_seen:
            citations_seen.add(url)
            citations.append(url)
        if len(citations) == 3:
            break

    if len(citations) < 1:
        raise ValueError("synthesize_answer:No citations found")

    for source in sources:
        title_name = source.get("title")
        if title_name and title_name not in titles_seen:
            titles_seen.add(title_name)
            titles.append(title_name)
            if len(titles) == 3:
                break

    if len(titles) < 1:
        raise ValueError("synthesize_answer:No titles found")

    bullet_block = ""
    for t in titles:
        bullet_block = bullet_block + "- " + t + "\n"


    answer = (
            f"Question: {question}\n"
            f"Based on the sources, here are the main angles to cover:\n"
            f"{bullet_block}\n"
            f"(Week 1 stub synthesis — real summarization comes in Week 2+)"
        )

    return {
        "answer": answer,
        "citations": citations,
        "status": "synthesized",
        }