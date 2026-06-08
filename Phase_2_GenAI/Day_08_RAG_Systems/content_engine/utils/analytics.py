"""
Content analytics utility module.
Computes word, character, sentence, and hashtag counts from generated text.
"""

import re
from dataclasses import dataclass


@dataclass
class ContentAnalytics:
    """Holds computed analytics for a piece of generated content."""

    word_count: int
    char_count: int
    sentence_count: int
    hashtag_count: int

    def to_dict(self) -> dict:
        return {
            "word_count": self.word_count,
            "char_count": self.char_count,
            "sentence_count": self.sentence_count,
            "hashtag_count": self.hashtag_count,
        }


def analyse(text: str) -> ContentAnalytics:
    """
    Compute analytics for the given text.

    Args:
        text: Generated content string.

    Returns:
        ContentAnalytics dataclass instance.
    """
    if not text or not text.strip():
        return ContentAnalytics(0, 0, 0, 0)

    words = len(text.split())
    chars = len(text)
    sentences = len(re.findall(r"[.!?]+", text)) or (1 if text.strip() else 0)
    hashtags = len(re.findall(r"#\w+", text))

    return ContentAnalytics(
        word_count=words,
        char_count=chars,
        sentence_count=sentences,
        hashtag_count=hashtags,
    )
