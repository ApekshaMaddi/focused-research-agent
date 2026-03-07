import json
from langchain.chat_models import init_chat_model
from focused_research_agent.config import get_llm_config


def get_llm():

    config = get_llm_config()
    llm = init_chat_model(
        model_provider=config["provider"],
        model=config["model"],
        temperature=config["temperature"],
        max_retries=config["max_retries"],
        api_key=config["api_key"],
    )
    return llm

def generate_json(prompt: str) -> dict:
    llm = get_llm()

    updated_prompt = prompt + "\nReturn ONLY valid JSON. No markdown. No backticks. No extra text."

    response = llm.invoke(updated_prompt)
    text = (response.content or "").strip()

    # 1) Remove triple-backtick fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        # drop first line (``` or ```json)
        if lines:
            lines = lines[1:]
        # drop last line if it's ```
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # 2) Try parsing directly first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3) Fallback: extract JSON object/array from surrounding text
    obj_start = text.find("{")
    obj_end = text.rfind("}")
    arr_start = text.find("[")
    arr_end = text.rfind("]")

    candidate = None
    if obj_start != -1 and obj_end != -1 and obj_start < obj_end:
        candidate = text[obj_start:obj_end + 1]
    elif arr_start != -1 and arr_end != -1 and arr_start < arr_end:
        candidate = text[arr_start:arr_end + 1]

    if candidate is None:
        raise ValueError(f"LLM did not return JSON. Raw output:\n{text[:400]}")

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}\nRaw output:\n{candidate[:400]}")

