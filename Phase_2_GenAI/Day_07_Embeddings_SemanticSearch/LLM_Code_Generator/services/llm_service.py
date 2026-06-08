"""
LLM service module.
Handles all communication with the Groq API.
"""

from groq import Groq, APIConnectionError, AuthenticationError, RateLimitError
from config import Config
from utils.logger import get_logger
from utils.token_counter import TokenCounter, TokenUsage

logger = get_logger(__name__)


class LLMService:
    """Service layer for interacting with the Groq LLM API."""

    def __init__(self) -> None:
        if not Config.GROQ_API_KEY:
            logger.error("GROQ_API_KEY is not set in environment variables.")
            raise EnvironmentError("GROQ_API_KEY is missing. Check your .env file.")
        self._client = Groq(api_key=Config.GROQ_API_KEY)
        self._model = Config.GROQ_MODEL
        logger.info("LLMService initialized | model=%s", self._model)

    def generate_code(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> tuple[str, TokenUsage]:
        """
        Send prompts to Groq and return generated code with token usage.

        Args:
            system_prompt: System-level instruction for the model.
            user_prompt: User-level task description and language instructions.
            temperature: Sampling temperature (lower = more deterministic).
            max_tokens: Maximum tokens in the completion.

        Returns:
            Tuple of (generated_code: str, token_usage: TokenUsage).

        Raises:
            RuntimeError: On API authentication, rate limit, or connection errors.
        """
        logger.info("Sending request to Groq | model=%s | max_tokens=%d", self._model, max_tokens)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            generated_code = response.choices[0].message.content or ""
            generated_code = self._clean_code(generated_code)

            # Prefer API-reported usage, fall back to estimation
            if response.usage:
                token_usage = TokenCounter.from_api_response(response.usage)
            else:
                token_usage = TokenCounter.estimate(user_prompt, generated_code)

            logger.info("Code generation successful | tokens_used=%d", token_usage.total_tokens)
            return generated_code, token_usage

        except AuthenticationError as exc:
            logger.error("Groq authentication failed: %s", exc)
            raise RuntimeError("Invalid Groq API key. Please check your GROQ_API_KEY.") from exc

        except RateLimitError as exc:
            logger.error("Groq rate limit exceeded: %s", exc)
            raise RuntimeError("Groq rate limit exceeded. Please wait and try again.") from exc

        except APIConnectionError as exc:
            logger.error("Groq connection error: %s", exc)
            raise RuntimeError("Cannot connect to Groq API. Check your internet connection.") from exc

        except Exception as exc:
            logger.error("Unexpected LLM error: %s", exc, exc_info=True)
            raise RuntimeError(f"Unexpected error during code generation: {exc}") from exc

    @staticmethod
    def _clean_code(raw: str) -> str:
        """
        Strip markdown fences from model output.

        Args:
            raw: Raw model output string.

        Returns:
            Clean code string without markdown fences.
        """
        lines = raw.strip().splitlines()
        # Remove opening fence (```python, ```js, ``` etc.)
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
