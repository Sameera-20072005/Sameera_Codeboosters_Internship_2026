"""
Facebook content generation chain.
Builds a LangChain pipeline for community-oriented Facebook posts.
"""

from services.groq_service import GroqService
from templates.prompts import FACEBOOK_TEMPLATE
from utils.logger import get_logger

logger = get_logger(__name__)


class FacebookChain:
    """LangChain-style chain for generating Facebook posts via Groq."""

    def __init__(self, groq_service: GroqService) -> None:
        self._groq = groq_service
        self._template = FACEBOOK_TEMPLATE

    def run(self, topic: str, tone: str, length: str) -> str:
        """
        Generate a Facebook post for the given topic.

        Args:
            topic: User-provided content topic.
            tone: Desired tone (friendly, casual, etc.).
            length: Desired length (short, medium, long).

        Returns:
            Generated Facebook post string.
        """
        prompt = self._template.format(topic=topic, tone=tone, length=length)
        logger.info("FacebookChain running | topic=%s | tone=%s | length=%s", topic, tone, length)
        return self._groq.generate_content(prompt, temperature=0.7)
