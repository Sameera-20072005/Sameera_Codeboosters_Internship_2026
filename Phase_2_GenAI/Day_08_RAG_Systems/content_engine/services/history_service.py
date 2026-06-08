"""
Content history service module.
Persists generated content to a JSON file and provides load/clear operations.

Fixes applied:
- datetime.now(timezone.utc) for timezone-aware timestamps
- load_history() no longer reverses in-memory before returning to save_content(),
  so the on-disk file always grows in chronological order; reversal only happens
  in the public read path
- Atomic write via a temp file to prevent JSON corruption on crash
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger(__name__)

_HISTORY_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "history.json")
)


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
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "platform": platform,
            "topic": topic,
            "tone": tone,
            "length": length,
            "content": content,
        }
        # Read raw chronological order (not reversed) then append
        existing = self._read_raw()
        existing.append(record)
        self._write(existing)
        logger.info("History saved | platform=%s | topic=%s", platform, topic)

    def load_history(self) -> list[dict]:
        """
        Load all history records, newest first.

        Returns:
            List of history record dicts sorted newest-first.
        """
        return list(reversed(self._read_raw()))

    def clear_history(self) -> None:
        """Wipe all history records."""
        self._write([])
        logger.info("History cleared.")

    # ── Private helpers ───────────────────────────────────────────────────────

    def _read_raw(self) -> list:
        """Read and return the raw chronological list from disk."""
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("History file is not a JSON array.")
            return data
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error("History file corrupted, resetting: %s", exc)
            self._write([])
            return []
        except FileNotFoundError:
            return []

    def _write(self, data: list) -> None:
        """
        Atomically write data list to the JSON history file.
        Uses a temp file + rename to prevent partial-write corruption.
        """
        dir_ = os.path.dirname(self._path)
        try:
            fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self._path)
        except OSError as exc:
            logger.error("Failed to write history: %s", exc)
            # Clean up temp file if rename failed
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
