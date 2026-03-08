
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm_config():
    provider = os.getenv("LLM_PROVIDER")
    model = os.getenv("LLM_MODEL")
    temp_raw = os.getenv("LLM_TEMPERATURE")
    retries_raw = os.getenv("LLM_MAX_RETRIES")
    api_key = os.getenv("LLM_API_KEY")

    if ((not provider or not provider.strip())
            or (not model or not model.strip())
            or ( not temp_raw or not temp_raw.strip())
            or (not retries_raw or not retries_raw.strip())
            or ( not api_key or not api_key.strip())):
        raise ValueError("Required values must be given in the .env file!")

    try:
        temperature = float(temp_raw)
    except ValueError:
        raise ValueError(f"LLM_TEMPERATURE must be a float. Got: {temp_raw}")

    try:
        max_retries = int(retries_raw)
    except ValueError:
        raise ValueError(f"MAX_RETRIES must be an int. Got: {retries_raw}")

    return {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "max_retries": max_retries,
        "api_key": api_key,
    }

