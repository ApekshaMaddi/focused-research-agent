import os
from dotenv import load_dotenv
#Preference given to groq if api keys of both groq and openai are present in .env file

load_dotenv()

LLM_TEMPERATURE_DEFAULT = 0.0
MAX_RETRIES_DEFAULT = 2

def get_llm_config():
    llm_config = {
        "mode": "llm_mode",
        "provider": None,
        "model": os.getenv("LLM_MODEL"),
        "temperature": float(os.getenv("LLM_TEMPERATURE")) | LLM_TEMPERATURE_DEFAULT,
        "max_retries": int(os.getenv("MAX_RETRIES")) | MAX_RETRIES_DEFAULT,
    }

    if (os.getenv("GROQ_API_KEY") is None) and (os.getenv("OPENAI_API_KEY") is None):
        llm_config = {
            "mode": "stub_mode",
            "model": None,
            "temperature": None,
            "max_retries": None,
        }

    elif (os.getenv("GROQ_API_KEY")) and (os.getenv("OPENAI_API_KEY") is None):
        llm_config["provider"] = "groq"

    elif (os.getenv("GROQ_API_KEY") is None) and (os.getenv("OPENAI_API_KEY")):
        llm_config["provider"] = "openai"

    elif (os.getenv("GROQ_API_KEY")) and (os.getenv("OPENAI_API_KEY")):
        llm_config["provider"] = "groq"

    return llm_config

