"""
Intent parser module.
Extracts structured project requirements from a natural language user request.
"""

from __future__ import annotations

import re
from services.llm_service import GroqLLMService
from utils.logger import get_logger

logger = get_logger(__name__)

# Valid values for enumerated fields
_VALID_LANGUAGES   = {"python", "javascript", "typescript", "java", "go", "rust", "c#", "c++"}
_VALID_VISIBILITY  = {"public", "private"}
_NAME_PATTERN      = re.compile(r"^[a-z0-9][a-z0-9\-]{0,38}$")


class IntentParser:
    """Parses a natural language project request into a structured intent dict."""

    def __init__(self, llm_service: GroqLLMService) -> None:
        self._llm = llm_service

    def parse(self, user_request: str) -> dict:
        """
        Extract and validate project intent from a natural language string.

        Args:
            user_request: Free-text project description from the user.

        Returns:
            Validated and sanitised intent dictionary.

        Raises:
            ValueError: If the user request is empty.
            RuntimeError: On LLM or JSON parse failure.
        """
        user_request = user_request.strip()
        if not user_request:
            raise ValueError("Project description cannot be empty.")

        logger.info("Parsing intent | request=%.80s", user_request)
        raw_intent = self._llm.parse_intent(user_request)
        intent     = self._validate(raw_intent)
        logger.info("Intent parsed | project=%s | lang=%s", intent["project_name"], intent["language"])
        return intent

    # ── Validation ────────────────────────────────────────────────────────────

    @staticmethod
    def _validate(intent: dict) -> dict:
        """
        Sanitise and apply defaults to the raw LLM-parsed intent.

        Args:
            intent: Raw dict from the LLM.

        Returns:
            Cleaned and defaulted intent dict.
        """
        # project_name: slug-safe
        name = str(intent.get("project_name", "my-project")).lower()
        name = re.sub(r"[^a-z0-9\-]", "-", name).strip("-")[:40] or "my-project"
        if not _NAME_PATTERN.match(name):
            name = "my-project"
        intent["project_name"] = name

        # description
        intent["description"] = str(intent.get("description", "A software project."))[:200]

        # language
        lang = str(intent.get("language", "Python")).strip()
        intent["language"] = lang if lang.lower() in _VALID_LANGUAGES else "Python"

        # framework — keep as-is, just ensure string
        intent["framework"] = str(intent.get("framework", "")).strip()

        # database
        intent["database"] = str(intent.get("database", "")).strip()

        # booleans
        for flag in ("testing_required", "docker_required", "ci_required"):
            val = intent.get(flag, False)
            intent[flag] = bool(val) if isinstance(val, bool) else str(val).lower() == "true"

        # visibility
        vis = str(intent.get("visibility", "public")).lower()
        intent["visibility"] = vis if vis in _VALID_VISIBILITY else "public"

        return intent
