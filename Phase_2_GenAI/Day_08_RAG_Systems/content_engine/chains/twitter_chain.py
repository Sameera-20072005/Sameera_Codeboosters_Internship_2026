"""
X (Twitter) content generation chain.
Builds a LangChain pipeline for concise, high-impact tweets.
"""

from services.groq_service import GroqService
from templates.prompts import TWITTER_TEMPLATE, sanitise_topic
from utils.logger import get_logger

logger = get_logger(__name__)


class TwitterChain:
    """LangChain-style chain for generating tweets via Groq."""

    def __init__(self, groq_service: GroqService) -> None:
        self._groq = groq_service
        self._template = TWITTER_TEMPLATE

    def run(self, topic: str, tone: str, length: str) -> str:
        """
        Generate a tweet for the given topic.

        Args:
            topic: User-provided content topic.
            tone: Desired tone (casual, humorous, professional, etc.).
            length: Desired length (short, medium, long thread).

        Returns:
            Generated tweet string.
        """
        safe_topic = sanitise_topic(topic)
        prompt = self._template.format_prompt(
            topic=safe_topic, tone=tone, length=length
        ).to_string()
        logger.info("TwitterChain running | tone=%s | length=%s", tone, length)
        return self._groq.generate_content(prompt, temperature=0.75, max_tokens=512)
