"""
Instagram content generation chain.
Builds a LangChain pipeline for engaging Instagram captions.
"""

from services.groq_service import GroqService
from templates.prompts import INSTAGRAM_TEMPLATE, sanitise_topic
from utils.logger import get_logger

logger = get_logger(__name__)


class InstagramChain:
    """LangChain-style chain for generating Instagram captions via Groq."""

    def __init__(self, groq_service: GroqService) -> None:
        self._groq = groq_service
        self._template = INSTAGRAM_TEMPLATE

    def run(self, topic: str, tone: str, length: str) -> str:
        """
        Generate an Instagram caption for the given topic.

        Args:
            topic: User-provided content topic.
            tone: Desired tone (casual, humorous, etc.).
            length: Desired length (short, medium, long).

        Returns:
            Generated Instagram caption string with hashtags.
        """
        safe_topic = sanitise_topic(topic)
        prompt = self._template.format_prompt(
            topic=safe_topic, tone=tone, length=length
        ).to_string()
        logger.info("InstagramChain running | tone=%s | length=%s", tone, length)
        return self._groq.generate_content(prompt, temperature=0.8)
