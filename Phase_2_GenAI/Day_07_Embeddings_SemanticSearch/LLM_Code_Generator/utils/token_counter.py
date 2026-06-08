"""
Token counting utility module.
Tracks prompt, response, and total token usage per request.
"""

from dataclasses import dataclass, field
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not available; falling back to word-based estimation.")


@dataclass
class TokenUsage:
    """Holds token counts for a single generation request."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    source: str = "api"  # "api" | "tiktoken" | "estimated"

    def to_dict(self) -> dict:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "source": self.source,
        }


class TokenCounter:
    """Utility class for counting and tracking token usage."""

    _ENCODING_NAME = "cl100k_base"  # compatible with GPT-4 / LLaMA family

    @classmethod
    def count_tokens(cls, text: str) -> int:
        """
        Count tokens in a text string.

        Args:
            text: Input text to count tokens for.

        Returns:
            Estimated token count.
        """
        if _TIKTOKEN_AVAILABLE:
            try:
                enc = tiktoken.get_encoding(cls._ENCODING_NAME)
                return len(enc.encode(text))
            except Exception as exc:
                logger.warning("tiktoken encoding failed: %s", exc)

        # Fallback: ~4 chars per token
        return max(1, len(text) // 4)

    @classmethod
    def from_api_response(cls, usage_obj) -> TokenUsage:
        """
        Build TokenUsage from a Groq API usage object.

        Args:
            usage_obj: Usage object returned by the Groq SDK.

        Returns:
            TokenUsage instance populated from API data.
        """
        try:
            prompt = getattr(usage_obj, "prompt_tokens", 0) or 0
            completion = getattr(usage_obj, "completion_tokens", 0) or 0
            total = getattr(usage_obj, "total_tokens", prompt + completion) or prompt + completion
            usage = TokenUsage(
                prompt_tokens=prompt,
                completion_tokens=completion,
                total_tokens=total,
                source="api",
            )
            logger.info("Token usage (API) — prompt: %d | completion: %d | total: %d",
                        prompt, completion, total)
            return usage
        except Exception as exc:
            logger.error("Failed to parse API token usage: %s", exc)
            return TokenUsage()

    @classmethod
    def estimate(cls, prompt: str, completion: str) -> TokenUsage:
        """
        Estimate token usage from raw text when API data is unavailable.

        Args:
            prompt: Prompt text sent to the model.
            completion: Completion text received from the model.

        Returns:
            TokenUsage instance with estimated counts.
        """
        prompt_tokens = cls.count_tokens(prompt)
        completion_tokens = cls.count_tokens(completion)
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            source="tiktoken" if _TIKTOKEN_AVAILABLE else "estimated",
        )
        logger.info("Token usage (estimated) — prompt: %d | completion: %d | total: %d",
                    prompt_tokens, completion_tokens, usage.total_tokens)
        return usage
