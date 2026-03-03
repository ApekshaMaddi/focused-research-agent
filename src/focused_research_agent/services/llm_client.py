import json

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from focused_research_agent.config import get_llm_config


load_dotenv()


def get_llm():

    config = get_llm_config()
    llm = None
    if config.get("mode") == "llm_mode" and config.get("provider") == "groq":
        llm = ChatGroq(
            model=config.get("model"),
            temperature=float(config.get("temperature")),
            max_retries=int(config.get("max_retries")),
        )
    elif config.get("mode") == "llm_mode" and config.get("provider") == "openai":
        llm = ChatOpenAI(
            model=config.get("model"),
            temperature=float(config.get("temperature")),
            max_retries=int(config.get("max_retries")),
          )
    elif config.get("mode") == "stub_mode":
         llm = None

    return llm

def generate_json(prompt: str) -> dict:
    llm = get_llm()
    updated_prompt = prompt +"\n Return the response only in valid JSON format."

    if llm is not None:
        response = llm.invoke(updated_prompt)
        text = response.content.strip()
        if text.__contains__("'''"):
            text=text.replace("'''","")
        final_response = json.loads(text)
    else:
        raise ValueError("Invalid response from LLM. Please try again.")
    return final_response

