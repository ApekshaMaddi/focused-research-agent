import json
from langchain.chat_models import init_chat_model
from focused_research_agent.config.llm_config import get_llm_config
from focused_research_agent.interfaces.llm_interface import LLMProvider
import logging

logger = logging.getLogger(__name__)


class GroqLLMProvider(LLMProvider):
    """Groq-backed implementation of the LLM provider contract."""

    def __init__(self):
        """Initialize the Groq LLM client using validated config."""
        self.llm_config = get_llm_config()

        self.llm = init_chat_model(
            model_provider=self.llm_config["provider"],
            model=self.llm_config["model"],
            temperature=self.llm_config["temperature"],
            max_retries=self.llm_config["max_retries"],
            api_key=self.llm_config["api_key"],
        )

    def generate_json(self, prompt: str) -> dict:
        """Generate structured JSON from a prompt using Groq.

        The method sends the prompt to the LLM, removes markdown-style
        code fences if present, and attempts strict JSON parsing with a
        fallback extraction pass.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            dict: Parsed JSON output from the LLM.

        Raises:
            ValueError: If the prompt is invalid or the provider does not
            return valid JSON.
        """

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("GroqLLMProvider: No prompt provided!")

        updated_prompt = (
            prompt
            + "\nReturn ONLY valid JSON. No markdown. No backticks. No extra text."
        )

        response = self.llm.invoke(updated_prompt)
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
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from LLM: {e}")

        # 3) Fallback: extract JSON object/array from surrounding text
        obj_start = text.find("{")
        obj_end = text.rfind("}")
        arr_start = text.find("[")
        arr_end = text.rfind("]")

        candidate = None
        if obj_start != -1 and obj_end != -1 and obj_start < obj_end:
            candidate = text[obj_start : obj_end + 1]
        elif arr_start != -1 and arr_end != -1 and arr_start < arr_end:
            candidate = text[arr_start : arr_end + 1]

        if candidate is None:
            raise ValueError(f"LLM did not return JSON. Raw output:\n{text[:400]}")

        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON from LLM: {e}\nRaw output:\n{candidate[:400]}"
            )
