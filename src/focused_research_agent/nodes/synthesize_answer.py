from focused_research_agent.state import ResearchState
from focused_research_agent.services import llm_client


def _collect_valid_sources(sources: list[dict]) -> list[dict]:
    valid_sources = list()

    for item in sources:
        if not isinstance(item, dict):
            continue

        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        snippet = (item.get("snippet") or "").strip()

        if not title or not url:
            continue

        valid_sources.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet,
            }
        )

    return valid_sources


def _build_synthesis_prompt(question: str, sources: list[dict]) -> str:
    source_blocks = list()

    for i, source in enumerate(sources, start=1):
        block = (
            f"Source {i}\n"
            f"Title: {source['title']}\n"
            f"URL: {source['url']}\n"
            f"Snippet: {source['snippet']}\n"
        )
        source_blocks.append(block)

    joined_sources = "\n".join(source_blocks)

    prompt = f"""
Return ONLY valid JSON. No markdown. No backticks. No extra text.

The JSON MUST have exactly these keys:
- answer (string)
- citations (list of 1 to 5 URLs)

Rules:
- Answer the user's question directly and clearly.
- Use ONLY the sources provided below.
- Do NOT invent facts.
- Do NOT invent citations.
- Every citation URL MUST come exactly from the provided source list.
- Keep the answer concise but useful.

Example JSON output:
{{
  "answer": "Ottawa is the capital of Canada.",
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

    return prompt


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

    prompt = _build_synthesis_prompt(question, synthesis_sources)
    response = llm_client.generate_json(prompt)

    if not isinstance(response, dict):
        raise ValueError("synthesize_answer: Invalid response obtained from LLM")

    answer = response.get("answer")
    citations = response.get("citations")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("synthesize_answer: Invalid answer obtained from LLM")

    if not isinstance(citations, list) or not citations:
        raise ValueError("synthesize_answer: Invalid citations obtained from LLM")

    cleaned_citations = []
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