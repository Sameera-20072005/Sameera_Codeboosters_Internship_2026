"""
YouTube content generation chain.
Builds a LangChain pipeline for SEO-optimised video titles and descriptions.
"""

from services.groq_service import GroqService
from templates.prompts import YOUTUBE_TEMPLATE
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeChain:
    """LangChain-style chain for generating YouTube video metadata via Groq."""

    def __init__(self, groq_service: GroqService) -> None:
        self._groq = groq_service
        self._template = YOUTUBE_TEMPLATE

    def run(self, topic: str, tone: str, length: str) -> str:
        """
        Generate a YouTube title, description, and hashtags for the given topic.

        Args:
            topic: User-provided video topic.
            tone: Desired tone (professional, casual, etc.).
            length: Desired video length type (short, medium, long).

        Returns:
            Generated YouTube metadata string.
        """
        prompt = self._template.format(topic=topic, tone=tone, length=length)
        logger.info("YouTubeChain running | topic=%s | tone=%s | length=%s", topic, tone, length)
        return self._groq.generate_content(prompt, temperature=0.65, max_tokens=1024)
