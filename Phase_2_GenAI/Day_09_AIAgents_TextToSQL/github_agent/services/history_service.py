"""
History service module.
Persists agent run records to data/history.json.
"""

from __future__ import annotations

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
    """Saves and loads agent execution history."""

    def __init__(self, path: str = _HISTORY_FILE) -> None:
        self._path = path
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        if not os.path.exists(self._path):
            self._write([])

    def save_history(
        self,
        request: str,
        repository_name: str,
        repository_url: str,
        intent: dict | None = None,
    ) -> None:
        """
        Append a new agent run record to history.

        Args:
            request:         Original user request string.
            repository_name: Name of the created repository.
            repository_url:  HTML URL of the repository.
            intent:          Parsed intent dict (optional).
        """
        record = {
            "timestamp":       datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "request":         request,
            "repository_name": repository_name,
            "repository_url":  repository_url,
            "intent":          intent or {},
        }
        existing = self._read_raw()
        existing.append(record)
        self._write(existing)
        logger.info("History saved | repo=%s", repository_name)

    def load_history(self) -> list[dict]:
        """Return all history records, newest first."""
        return list(reversed(self._read_raw()))

    def clear_history(self) -> None:
        """Remove all stored history records."""
        self._write([])
        logger.info("History cleared.")

    # ── Private ───────────────────────────────────────────────────────────────

    def _read_raw(self) -> list:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write(self, data: list) -> None:
        dir_ = os.path.dirname(self._path)
        try:
            fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self._path)
        except OSError as exc:
            logger.error("Failed to write history: %s", exc)
            try:
                os.unlink(tmp)
            except OSError:
                pass
