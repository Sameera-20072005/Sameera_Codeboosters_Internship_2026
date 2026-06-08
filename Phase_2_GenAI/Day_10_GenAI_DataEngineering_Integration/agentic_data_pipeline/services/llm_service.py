"""
Groq LLM service — dataset generation and business-insight generation.
"""
from __future__ import annotations

import os
import re
import time
from dotenv import load_dotenv
from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_MODEL      = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_TIMEOUT    = 60          # seconds
_MAX_TOKENS = 4096
_MAX_INPUT  = 4000        # char cap on user input
_MAX_RETRY  = 3
_RETRY_WAIT = 5           # seconds between retries


class GroqService:
    """Handles all Groq LLM interactions for the agentic pipeline."""

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY is missing. Check your .env file.")
        self._client = Groq(api_key=api_key, timeout=_TIMEOUT)
        self._model  = _MODEL
        logger.info("GroqService initialised | model=%s", self._model)

    # ── Public ────────────────────────────────────────────────────────────────

    def generate_dataset(self, prompt: str, record_count: int) -> str:
        """
        Ask the LLM to generate a CSV dataset.

        Args:
            prompt:       Natural language dataset description.
            record_count: Number of data rows to generate.

        Returns:
            Raw CSV string (header + rows).
        """
        system = (
            "You are an expert data engineer. Generate ONLY raw CSV data with a header row. "
            "No explanation, no markdown fences, no commentary — just CSV."
        )
        user = (
            f"{prompt[:_MAX_INPUT]}\n\n"
            f"Generate exactly {record_count} data rows (plus 1 header row). "
            "Use realistic, varied values. Output CSV only."
        )
        logger.info("Generating dataset | records=%d", record_count)
        return self._call(system, user, max_tokens=min(_MAX_TOKENS, record_count * 6 + 200))

    def generate_insights(self, kpis: dict, dataset_description: str) -> str:
        """
        Generate business insights from KPI data using the LLM.

        Args:
            kpis:                Computed KPI dictionary.
            dataset_description: Original user description for context.

        Returns:
            Markdown-formatted insights string.
        """
        import json
        kpi_text = json.dumps(kpis, indent=2, default=str)[:2000]
        system = (
            "You are a senior business analyst. Analyse the KPIs and generate "
            "3-5 concise, actionable business insights in Markdown bullet format."
        )
        user = (
            f"Dataset context: {dataset_description[:500]}\n\n"
            f"KPIs:\n{kpi_text}\n\n"
            "Generate insights:"
        )
        logger.info("Generating LLM insights")
        return self._call(system, user, max_tokens=1024)

    # ── Private ───────────────────────────────────────────────────────────────

    def _call(self, system: str, user: str, max_tokens: int = _MAX_TOKENS) -> str:
        """Send a chat completion request with retry logic."""
        for attempt in range(1, _MAX_RETRY + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                    temperature=0.4,
                    max_tokens=min(max_tokens, _MAX_TOKENS),
                )
                content = (response.choices[0].message.content or "").strip()
                if not content:
                    raise RuntimeError("LLM returned empty response.")
                content = self._strip_fences(content)
                logger.debug("LLM call OK | tokens=%s", getattr(response.usage, "total_tokens", "?"))
                return content

            except RateLimitError:
                if attempt < _MAX_RETRY:
                    logger.warning("Rate limited — waiting %ds (attempt %d)", _RETRY_WAIT, attempt)
                    time.sleep(_RETRY_WAIT * attempt)
                else:
                    raise RuntimeError("Groq rate limit exceeded after retries.") from None

            except AuthenticationError as exc:
                raise RuntimeError("Invalid GROQ_API_KEY.") from exc

            except APIConnectionError as exc:
                raise RuntimeError("Cannot reach Groq API. Check your connection.") from exc

            except RuntimeError:
                raise

            except Exception as exc:
                raise RuntimeError(f"Unexpected LLM error: {exc}") from exc

        raise RuntimeError("LLM call failed after all retries.")

    @staticmethod
    def _strip_fences(text: str) -> str:
        """Remove markdown code fences."""
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
        text = re.sub(r"\n?```$",          "", text.strip())
        return text.strip()
