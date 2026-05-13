"""
Groq-backed implementation of the LLM provider contract.

This module provides the GroqLLMProvider class which implements the
LLMProvider interface using LangChain's init_chat_model with the Groq
provider. It handles prompt validation, JSON-only instruction appending,
code fence stripping, and fallback JSON extraction from surrounding text.

The JSON parsing pipeline works in two stages:
1. Direct json.loads on the cleaned response text
2. If that fails, extract the first JSON object or array substring and
   attempt to parse that instead

Static helpers are used for all pure transformation functions that do
not require instance state, following the same pattern as the rest of
the project.

Architecturally, this module belongs to the services layer and implements
the Adapter pattern — it translates between the LangChain/Groq API and
the internal LLMProvider interface used throughout the project.
"""

import json
import logging

from langchain.chat_models import init_chat_model

from focused_research_agent.config.llm_config import get_llm_config
from focused_research_agent.interfaces.llm_interface import LLMProvider

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
            max_tokens=self.llm_config["max_tokens"],
        )

    # ------------------------------------------------------------------
    # Static helpers — pure functions that support the provider but do
    # not read or modify any instance state. @staticmethod signals this
    # intent explicitly and prevents accidental use of self.
    # ------------------------------------------------------------------

    @staticmethod
    def _build_json_only_prompt(prompt: str) -> str:
        """Validate the prompt and append a strict JSON-only instruction.

        Args:
            prompt: The raw prompt to send to the LLM.

        Returns:
            str: The validated prompt with an added JSON-only instruction.

        Raises:
            ValueError: If the prompt is not a non-empty string.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("GroqLLMProvider: No prompt provided!")

        return (
            prompt
            + "\nReturn ONLY valid JSON. No markdown. No backticks. No extra text."
        )

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Remove surrounding triple-backtick code fences from LLM output.

        This handles responses such as ```json ... ``` and returns the
        inner content unchanged when no code fences are present.

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

        The method looks for the outermost JSON object first and, if not
        found, falls back to a JSON array.

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

    @staticmethod
    def _extract_text_from_content(content: str | list) -> str:
        """Extract a plain text string from a LangChain response content value.

        LangChain declares response.content as str | list[Any]. The str
        branch is the normal path for text-only models such as Groq. The
        list branch carries multi-modal content blocks (dicts with a "text"
        key) used by vision or audio-capable models. This method handles
        both branches so the rest of generate_json always works with a
        plain string.

        Args:
            content: Raw content value returned by the LangChain response
                object. Either a plain string or a list of content block
                dicts.

        Returns:
            str: Plain text extracted from the content value. Returns an
                empty string if the content is neither a str nor a list.
        """
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            # Each block is typically {"type": "text", "text": "..."}.
            # Fall back to str(block) for any non-dict items.
            text_parts = []

            for block in content:
                if isinstance(block, dict):
                    text_parts.append(block.get("text", ""))
                else:
                    text_parts.append(str(block))

            return "".join(text_parts)

        return ""

    # ------------------------------------------------------------------
    # Instance method — uses self.llm (instance state) to invoke the
    # model, and calls the static helpers above.
    # ------------------------------------------------------------------

    def generate_json(self, prompt: str) -> dict:
        """Generate structured JSON from a prompt using Groq.

        The method validates the prompt, appends a JSON-only instruction,
        invokes the LLM, removes code fences if present, and first tries
        direct JSON parsing. If that fails, it attempts to extract a JSON
        object or array from surrounding text and parse that instead.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            dict: Parsed JSON output from the LLM.

        Raises:
            ValueError: If the prompt is invalid or the provider does not
                return recoverable valid JSON.
        """
        updated_prompt = self._build_json_only_prompt(prompt)
        logger.info("Invoking Groq LLM with model: %s", self.llm_config["model"])
        response = self.llm.invoke(updated_prompt)

        raw_text = self._extract_text_from_content(response.content)
        text = self._strip_code_fences(raw_text.strip())

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.exception("Invalid JSON from LLM: %s", e)

        candidate = self._extract_json_candidate(text)

        if candidate is None:
            raise ValueError(f"LLM did not return JSON. Raw output:\n{text[:400]}")

        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            logger.exception(
                "Invalid JSON from LLM: %s\nRaw output:\n%s", e, candidate[:400]
            )
            raise ValueError(
                f"Invalid JSON from LLM: {e}\nRaw output:\n{candidate[:400]}"
            )
