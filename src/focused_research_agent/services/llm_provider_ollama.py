"""
Ollama-backed implementation of the LLM provider contract.

Supports both local Ollama instances and Ollama Cloud API.
When LLM_API_KEY is set, requests are routed to Ollama Cloud.
"""

import json
import logging

from ollama import Client

from focused_research_agent.config.llm_config import get_llm_config
from focused_research_agent.interfaces.llm_interface import LLMProvider

logger = logging.getLogger(__name__)


class OllamaLLMProvider(LLMProvider):
    """Ollama-backed implementation of the LLM provider contract."""

    def __init__(self):
        """Initialize the Ollama client using validated config."""
        self.llm_config = get_llm_config()

        api_key = self.llm_config.get("api_key")

        if api_key and api_key.strip() and api_key != "not-needed":
            self.client = Client(
                host="https://ollama.com",
                headers={"Authorization": f"Bearer {api_key}"},
            )
        else:
            self.client = Client()

        self.model = self.llm_config["model"]

    def generate_json(self, prompt: str) -> dict:
        """Generate structured JSON from a prompt using Ollama.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            dict: Parsed JSON output from the LLM.

        Raises:
            ValueError: If the prompt is invalid or the provider does
                not return recoverable valid JSON.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("OllamaLLMProvider: No prompt provided!")

        logger.info("Invoking Ollama LLM with model: %s", self.model)

        updated_prompt = (
            prompt
            + "\nReturn ONLY valid JSON. No markdown. No backticks. No extra text."
        )

        response = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": updated_prompt}],
        )

        raw_text = response.message.content.strip()
        text = self._strip_code_fences(raw_text)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from LLM: {e}")

        candidate = self._extract_json_candidate(text)

        if candidate is None:
            raise ValueError(f"LLM did not return JSON. Raw output:\n{text[:400]}")

        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON from LLM: {e}\nRaw output:\n{candidate[:400]}"
            )

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Remove surrounding triple-backtick code fences from LLM output.

        Args:
            text: Raw text returned by the LLM.

        Returns:
            str: Text with outer code fences removed when present.
        """
        if text.startswith("```"):
            lines = text.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return text

    @staticmethod
    def _extract_json_candidate(text: str) -> str | None:
        """Extract a likely JSON object or array substring from mixed text.

        Args:
            text: LLM output that may contain JSON surrounded by extra text.

        Returns:
            str | None: The extracted JSON substring if found, otherwise None.
        """
        obj_start = text.find("{")
        obj_end = text.rfind("}")
        arr_start = text.find("[")
        arr_end = text.rfind("]")

        if obj_start != -1 and obj_end != -1 and obj_start < obj_end:
            return text[obj_start : obj_end + 1]

        if arr_start != -1 and arr_end != -1 and arr_start < arr_end:
            return text[arr_start : arr_end + 1]

        return None
