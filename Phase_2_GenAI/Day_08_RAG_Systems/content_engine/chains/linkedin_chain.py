"""
LinkedIn content generation chain.
Builds a LangChain pipeline for professional LinkedIn posts.
"""

from services.groq_service import GroqService
from templates.prompts import LINKEDIN_TEMPLATE
from utils.logger import get_logger

logger = get_logger(__name__)


class LinkedInChain:
    """LangChain-style chain for generating LinkedIn posts via Groq."""

    def __init__(self, groq_service: GroqService) -> None:
        self._groq = groq_service
        self._template = LINKEDIN_TEMPLATE

    def run(self, topic: str, tone: str, length: str) -> str:
        """
        Generate a LinkedIn post for the given topic.

        Args:
            topic: User-provided content topic.
            tone: Desired tone (professional, friendly, etc.).
            length: Desired length (short, medium, long).

        Returns:
            Generated LinkedIn post string.
        """
        prompt = self._template.format(topic=topic, tone=tone, length=length)
        logger.info("LinkedInChain running | topic=%s | tone=%s | length=%s", topic, tone, length)
        return self._groq.generate_content(prompt, temperature=0.6)
