"""
Groq API service module.
Handles all LLM communication via the Groq Python SDK.
"""

import os
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, AuthenticationError, RateLimitError
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Hard caps to prevent unbounded resource consumption (CWE-400)
_MAX_TOKENS_HARD_CAP = 2048
_MAX_INPUT_CHARS = 4000
_REQUEST_TIMEOUT = 30  # seconds


class GroqService:
    """Service layer for generating content through the Groq LLM API."""

    def __init__(self) -> None:
        self._api_key = os.getenv("GROQ_API_KEY", "")
        if not self._api_key:
            logger.error("GROQ_API_KEY is not set.")
            raise EnvironmentError("GROQ_API_KEY is missing. Check your .env file.")
        # Pass timeout at the client level so every request inherits it
        self._client = Groq(api_key=self._api_key, timeout=_REQUEST_TIMEOUT)
        self._model = _MODEL
        logger.info("GroqService initialised | model=%s", self._model)

    def validate_connection(self) -> bool:
        """
        Validate that the Groq API key is functional with a minimal probe call.

        Returns:
            True if the API is reachable and authenticated, False otherwise.
        """
        try:
            self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
                temperature=0.0,
            )
            logger.info("Groq connection validated successfully.")
            return True
        except Exception as exc:
            logger.error("Groq connection validation failed: %s", exc)
            return False

    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Send a formatted prompt to Groq and return the generated text.

        Args:
            prompt: Fully rendered prompt string (max 4000 chars enforced).
            temperature: Sampling temperature (higher = more creative).
            max_tokens: Maximum tokens in the completion (capped at 2048).

        Returns:
            Clean generated content string.

        Raises:
            ValueError: If the prompt is empty or exceeds the input limit.
            RuntimeError: On authentication, rate limit, or connection errors.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        # Enforce input length limit to prevent unbounded consumption
        if len(prompt) > _MAX_INPUT_CHARS:
            raise ValueError(
                f"Prompt too long ({len(prompt)} chars). Maximum is {_MAX_INPUT_CHARS}."
            )

        # Clamp max_tokens to the hard cap
        safe_max_tokens = min(max_tokens, _MAX_TOKENS_HARD_CAP)

        logger.info("Sending prompt to Groq | length=%d chars | max_tokens=%d", len(prompt), safe_max_tokens)
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert social media content creator. "
                            "Generate only the requested content with no extra commentary, "
                            "no markdown fences, and no preamble."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=safe_max_tokens,
            )
            content = response.choices[0].message.content or ""
            if not content.strip():
                logger.warning("Groq returned an empty response.")
                raise RuntimeError("The model returned an empty response. Please try again.")
            content = self._clean(content)
            logger.info(
                "Content generated | tokens=%s",
                getattr(response.usage, "total_tokens", "?"),
            )
            return content

        except AuthenticationError as exc:
            logger.error("Groq auth error: %s", exc)
            raise RuntimeError("Invalid Groq API key. Please check your GROQ_API_KEY.") from exc

        except RateLimitError as exc:
            logger.error("Groq rate limit: %s", exc)
            raise RuntimeError("Groq rate limit exceeded. Please wait and retry.") from exc

        except APIConnectionError as exc:
            logger.error("Groq connection error: %s", exc)
            raise RuntimeError("Cannot reach Groq API. Check your internet connection.") from exc

        except (ValueError, RuntimeError):
            raise  # re-raise our own validated errors without wrapping

        except Exception as exc:
            logger.error("Unexpected Groq error: %s", exc, exc_info=True)
            raise RuntimeError(f"Unexpected error during generation: {exc}") from exc

    @staticmethod
    def _clean(text: str) -> str:
        """Strip markdown fences from model output."""
        lines = text.strip().splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
