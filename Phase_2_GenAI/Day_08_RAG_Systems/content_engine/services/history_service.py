"""
Content history service module.
Persists generated content to a JSON file and provides load/clear operations.
"""

import json
import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "history.json")
_HISTORY_FILE = os.path.abspath(_HISTORY_FILE)


class HistoryService:
    """Manages reading and writing content generation history to JSON."""

    def __init__(self, path: str = _HISTORY_FILE) -> None:
        self._path = path
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        if not os.path.exists(self._path):
            self._write([])

    # ── Public API ────────────────────────────────────────────────────────────

    def save_content(
        self,
        platform: str,
        topic: str,
        tone: str,
        length: str,
        content: str,
    ) -> None:
        """
        Append a generation record to the history file.

        Args:
            platform: Target social media platform.
            topic: User-provided topic.
            tone: Selected tone.
            length: Selected content length.
            content: Generated content string.
        """
        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "platform": platform,
            "topic": topic,
            "tone": tone,
            "length": length,
            "content": content,
        }
        history = self.load_history()
        history.append(record)
        self._write(history)
        logger.info("History saved | platform=%s | topic=%s", platform, topic)

    def load_history(self) -> list[dict]:
        """
        Load all history records from the JSON file.

        Returns:
            List of history record dicts, newest first.
        """
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("History file is not a JSON array.")
            return list(reversed(data))
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error("History file corrupted, resetting: %s", exc)
            self._write([])
            return []
        except FileNotFoundError:
            return []

    def clear_history(self) -> None:
        """Wipe all history records."""
        self._write([])
        logger.info("History cleared.")

    # ── Private helpers ───────────────────────────────────────────────────────

    def _write(self, data: list) -> None:
        """Write data list to the JSON history file."""
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as exc:
            logger.error("Failed to write history: %s", exc)
