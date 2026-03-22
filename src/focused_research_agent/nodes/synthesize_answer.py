from focused_research_agent.state import ResearchState
from focused_research_agent.services.llm_factory import get_llm_provider
from urllib.parse import urlparse


# Hardcoding a small list of trusted and weak domains is okay as a quick experiment, but it is not a scalable long-term design. An interviewer could absolutely ask that.
#
# A good answer in an interview would be:
#
# this was a lightweight prototype heuristic to improve citation quality quickly
# it was never meant to be a complete trust model
# hardcoding every domain would not scale and would be hard to maintain
# a better production direction would be:
# configurable rules in settings/data files
# broader heuristics based on source type and metadata
# possibly provider-side ranking/filtering
# or a separate source-quality evaluation component

def _extract_domain(url: str) -> str:
    domain = urlparse(url).netloc.lower().strip()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def _matches_domain(domain: str, target: str) -> bool:
    return domain == target or domain.endswith("." + target)


def _get_domain_bonus(domain: str) -> float:
    if domain.endswith(".gov"):
        return 4.0

    if domain.endswith(".edu"):
        return 3.5

    trusted_domains = {
        "britannica.com": 3.0,
        "timeanddate.com": 3.0,
        "metoffice.gov.uk": 3.0,
        "weather.gov": 3.0,
        "noaa.gov": 3.0,
    }

    weak_domains = {
        "youtube.com": -3.0,
        "medium.com": -3.0,
        "reddit.com": -3.0,
        "quora.com": -3.0,
        "facebook.com": -3.0,
        "tiktok.com": -3.0,
        "instagram.com": -3.0,
    }

    for trusted_domain, bonus in trusted_domains.items():
        if _matches_domain(domain, trusted_domain):
            return bonus

    for weak_domain, penalty in weak_domains.items():
        if _matches_domain(domain, weak_domain):
            return penalty

    return 0.0

def _is_weak_domain(domain: str) -> bool:
    weak_domains = {
        "youtube.com",
        "medium.com",
        "reddit.com",
        "quora.com",
        "facebook.com",
        "tiktok.com",
        "instagram.com",
    }

    for weak_domain in weak_domains:
        if _matches_domain(domain, weak_domain):
            return True

    return False


def _filter_sources_for_synthesis(valid_sources: list[dict]) -> list[dict]:
    strong_or_neutral_sources = []

    for source in valid_sources:
        domain = _extract_domain(source["url"])

        if not _is_weak_domain(domain):
            strong_or_neutral_sources.append(source)

    if len(strong_or_neutral_sources) >= 4:
        return strong_or_neutral_sources

    return valid_sources

def _get_rank_score(source: dict) -> float:
    domain = _extract_domain(source["url"])
    bonus = _get_domain_bonus(domain)
    return source["score"] + bonus



def _collect_valid_sources(sources: list[dict]) -> list[dict]:
    valid_sources = list()

    for item in sources:
        if not isinstance(item, dict):
            continue

        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        snippet = (item.get("snippet") or "").strip()
        source_name = (item.get("source") or "").strip()
        score = item.get("score", 0.0)

        if not title or not url or not snippet:
            continue

        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0

        valid_sources.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": source_name,
                "score": score,
            }
        )

    if not valid_sources:
        return list()

    valid_sources = sorted(valid_sources, key=_get_rank_score, reverse=True)
    return valid_sources


def _build_synthesis_prompt(question: str, sources: list[dict]) -> str:
    source_blocks = []

    for index, source in enumerate(sources, start=1):
        source_block = (
            f"Source {index}\n"
            f"Title: {source['title']}\n"
            f"URL: {source['url']}\n"
            f"Snippet: {source['snippet']}\n"
        )
        source_blocks.append(source_block)

    joined_sources = "\n".join(source_blocks)

    return f"""
 Return ONLY valid JSON. No markdown. No backticks. No extra text.

 The JSON MUST have exactly these keys:
 - answer (string)
 - citations (list of 1 to 3 URLs)

 Rules:
 - Answer the user's question directly in the first sentence.
 - Then add 2 to 3 short supporting sentences.
 - Keep the answer clear, natural, and concise.
 - Avoid repetition.
 - Prefer the strongest and most trustworthy sources.
 - Prefer official, educational, scientific, or well-known reference sources when available.
 - Use ONLY the sources provided below.
 - Do NOT invent facts.
 - Do NOT invent citations.
 - Every citation URL MUST match one of the provided source URLs exactly.
 - Choose the best 2 to 3 citations, not just any valid citations.
 - Do NOT mention "sources", "snippets", or "citations" inside the answer.

 Example JSON output:
 {{
   "answer": "An equinox is when day and night are nearly equal in length, while a solstice is when the Sun reaches its highest or lowest point in the sky, creating the longest or shortest day of the year. Equinoxes mark the start of spring and autumn. Solstices mark the start of summer and winter.",
   "citations": [
     "https://example.com/source1",
     "https://example.com/source2"
   ]
 }}

 User question:
 {question}

 Sources:
 {joined_sources}
 """.strip()

def synthesize_answer(state: ResearchState) -> dict:
    question = (state.get("question") or "").strip()
    sources = state.get("sources")

    if not question:
        raise ValueError("synthesize_answer: No question found")

    if not isinstance(sources, list) or not sources:
        raise ValueError("synthesize_answer: No sources found")

    valid_sources = _collect_valid_sources(sources)

    if not valid_sources:
        raise ValueError("synthesize_answer: No valid sources found")

    synthesis_sources = valid_sources[:6]
    allowed_urls = {source["url"] for source in synthesis_sources}

    llm_provider = get_llm_provider()
    prompt = _build_synthesis_prompt(question, synthesis_sources)
    response = llm_provider.generate_json(prompt)

    if not isinstance(response, dict):
        raise ValueError("synthesize_answer: Invalid response obtained from LLM")

    answer = response.get("answer")
    citations = response.get("citations")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("synthesize_answer: Invalid answer obtained from LLM")

    if not isinstance(citations, list) or not citations:
        raise ValueError("synthesize_answer: Invalid citations obtained from LLM")

    cleaned_citations = list()
    seen_citations = set()

    for citation in citations:
        if not isinstance(citation, str):
            raise ValueError("synthesize_answer: Citation must be a string")

        citation = citation.strip()

        if not citation:
            raise ValueError("synthesize_answer: Empty citation returned by LLM")

        if citation not in allowed_urls:
            raise ValueError(
                f"synthesize_answer: LLM returned unknown citation URL: {citation}"
            )

        if citation not in seen_citations:
            seen_citations.add(citation)
            cleaned_citations.append(citation)

    if not cleaned_citations:
        raise ValueError("synthesize_answer: No valid citations found")

    return {
        "answer": answer.strip(),
        "citations": cleaned_citations,
        "status": "synthesized",
    }