"""
LLM service module.
Uses Groq API with LangChain to parse intent and generate project artefacts.
"""

from __future__ import annotations

import json
import os
import re
from dotenv import load_dotenv
from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError
from langchain_core.prompts import PromptTemplate
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_MODEL          = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_MAX_TOKENS     = 2048
_INPUT_CHAR_CAP = 3000
_TIMEOUT        = 30

# ── Module-level prompt templates (compiled once, not on every call) ──────────
_INTENT_TEMPLATE = PromptTemplate(
    input_variables=["request"],
    template=(
        "You are a software architect assistant. Analyse the following project request "
        "and return ONLY a valid JSON object — no prose, no fences.\n\n"
        "Required JSON fields:\n"
        "  project_name    (string, lowercase-hyphenated, max 40 chars)\n"
        "  description     (string, one sentence)\n"
        "  language        (string, e.g. Python, JavaScript, Java)\n"
        "  framework       (string or empty string)\n"
        "  database        (string or empty string)\n"
        "  testing_required  (boolean)\n"
        "  docker_required   (boolean)\n"
        "  ci_required       (boolean)\n"
        "  visibility        (string: public or private)\n\n"
        "Project request:\n{request}\n\n"
        "JSON:"
    ),
)

_README_TEMPLATE = PromptTemplate(
    input_variables=["intent"],
    template=(
        "You are a technical writer. Generate a professional README.md for the following project.\n"
        "Return only the markdown — no fences.\n\n"
        "Project details:\n{intent}\n\n"
        "README.md:"
    ),
)

_STRUCTURE_TEMPLATE = PromptTemplate(
    input_variables=["intent"],
    template=(
        "You are a software architect. Given the project details below, return ONLY a JSON array "
        "of relative file paths to create (strings only, no objects). Include src/, tests/ if needed, "
        "docs/index.md, and any framework-specific files. No explanation.\n\n"
        "Project: {intent}\n\n"
        "JSON array:"
    ),
)

_REQUIREMENTS_TEMPLATE = PromptTemplate(
    input_variables=["language", "framework", "database", "testing"],
    template=(
        "Generate a {language} requirements.txt (one package per line, no versions unless critical). "
        "Framework: {framework}. Database: {database}. Testing required: {testing}.\n"
        "Return ONLY the file contents — no explanation, no fences."
    ),
)


class GroqLLMService:
    """Handles all LLM interactions via Groq for the GitHub Agent."""

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY is missing. Check your .env file.")
        self._client = Groq(api_key=api_key, timeout=_TIMEOUT)
        self._model  = _MODEL
        logger.info("GroqLLMService initialised | model=%s", self._model)

    # ── Public methods ────────────────────────────────────────────────────────

    def parse_intent(self, user_request: str) -> dict:
        """
        Extract structured project intent from a natural language request.

        Args:
            user_request: Free-text project description from the user.

        Returns:
            Dict with keys: project_name, description, language, framework,
            database, testing_required, docker_required, ci_required, visibility.

        Raises:
            RuntimeError: On API or JSON parsing failure.
        """
        # Escape braces in user input before passing to PromptTemplate
        safe_request = self._escape_braces(self._cap(user_request))
        prompt = _INTENT_TEMPLATE.format_prompt(request=safe_request).to_string()
        raw = self._call(prompt)
        return self._parse_json(raw, "intent")

    def generate_readme(self, intent: dict) -> str:
        """
        Generate a README.md body using the LLM.

        Args:
            intent: Parsed project intent dict.

        Returns:
            Markdown README string.
        """
        # Escape braces in the serialised intent JSON to prevent PromptTemplate KeyError
        safe_intent = self._escape_braces(json.dumps(intent, indent=2))
        prompt = _README_TEMPLATE.format_prompt(intent=safe_intent).to_string()
        return self._call(prompt, max_tokens=1024)

    def generate_folder_structure(self, intent: dict) -> list[str]:
        """
        Generate a list of relative file/folder paths for the project.

        Args:
            intent: Parsed project intent dict.

        Returns:
            List of path strings (e.g. ['src/main.py', 'tests/test_main.py']).
        """
        safe_intent = self._escape_braces(json.dumps(intent, indent=2))
        prompt = _STRUCTURE_TEMPLATE.format_prompt(intent=safe_intent).to_string()
        raw = self._call(prompt, max_tokens=512)
        return self._parse_json_list(raw)

    def generate_requirements(self, intent: dict) -> str:
        """
        Generate a requirements.txt based on intent.

        Args:
            intent: Parsed project intent dict.

        Returns:
            String contents of the requirements file.
        """
        prompt = _REQUIREMENTS_TEMPLATE.format_prompt(
            language=self._escape_braces(intent.get("language", "Python")),
            framework=self._escape_braces(intent.get("framework", "")),
            database=self._escape_braces(intent.get("database", "")),
            testing=str(intent.get("testing_required", False)),
        ).to_string()
        return self._call(prompt, max_tokens=256)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _call(self, prompt: str, max_tokens: int = _MAX_TOKENS) -> str:
        """Send a prompt to Groq and return stripped response text."""
        logger.debug("LLM call | prompt_len=%d", len(prompt))
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise software engineering assistant. "
                            "Follow instructions exactly. Return only what is asked."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=min(max_tokens, _MAX_TOKENS),
            )
            content = (response.choices[0].message.content or "").strip()
            if not content:
                raise RuntimeError("LLM returned an empty response.")
            logger.debug(
                "LLM response | tokens=%s",
                getattr(response.usage, "total_tokens", "?"),
            )
            return content
        except AuthenticationError as exc:
            raise RuntimeError("Invalid GROQ_API_KEY.") from exc
        except RateLimitError as exc:
            raise RuntimeError("Groq rate limit exceeded. Please wait.") from exc
        except APIConnectionError as exc:
            raise RuntimeError("Cannot reach Groq API. Check your connection.") from exc
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Unexpected LLM error: {exc}") from exc

    @staticmethod
    def _cap(text: str) -> str:
        """Truncate input to the character cap to prevent unbounded consumption."""
        return text[:_INPUT_CHAR_CAP]

    @staticmethod
    def _escape_braces(text: str) -> str:
        """
        Escape literal curly braces so they don't break PromptTemplate substitution.
        LangChain uses single { } for variables; {{ }} renders as a literal brace.
        """
        return text.replace("{", "{{").replace("}", "}}")

    @staticmethod
    def _strip_fences(text: str) -> str:
        """Remove markdown code fences from LLM output."""
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
        text = re.sub(r"\n?```$", "", text.strip())
        return text.strip()

    def _parse_json(self, raw: str, label: str) -> dict:
        """
        Parse a JSON object from raw LLM output.

        Args:
            raw:   Raw LLM response string.
            label: Human-readable label for error messages.

        Returns:
            Parsed dict.

        Raises:
            RuntimeError: On JSON decode failure.
        """
        cleaned = self._strip_fences(raw)
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        try:
            result = json.loads(cleaned)
            if not isinstance(result, dict):
                raise ValueError("Expected a JSON object.")
            return result
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error(
                "JSON parse failed for %s: %s | raw=%.200s", label, exc, raw
            )
            raise RuntimeError(
                f"LLM returned invalid JSON for {label}: {exc}"
            ) from exc

    def _parse_json_list(self, raw: str) -> list[str]:
        """Parse a JSON array of strings from raw LLM output."""
        cleaned = self._strip_fences(raw)
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        try:
            result = json.loads(cleaned)
            if isinstance(result, list):
                return [str(p) for p in result]
            raise ValueError("Expected a JSON array.")
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error("JSON list parse failed: %s | raw=%.200s", exc, raw)
            return ["src/main.py", "tests/test_main.py", "docs/index.md"]
