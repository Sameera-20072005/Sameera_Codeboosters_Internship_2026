"""
Storage service — centralised I/O for CSV, JSON, and text artefacts.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _abs(rel: str) -> str:
    return os.path.join(_BASE, rel)


class StorageService:
    """Centralised file I/O for the pipeline."""

    # ── DataFrame ─────────────────────────────────────────────────────────────

    @staticmethod
    def save_dataframe(df: pd.DataFrame, rel_path: str) -> str:
        """
        Save a DataFrame as CSV.

        Args:
            df:       DataFrame to save.
            rel_path: Path relative to project root.

        Returns:
            Absolute path of the saved file.
        """
        path = _abs(rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        logger.info("Saved DataFrame | rows=%d | path=%s", len(df), path)
        return path

    @staticmethod
    def load_dataframe(rel_path: str) -> pd.DataFrame:
        """
        Load a CSV file into a DataFrame.

        Args:
            rel_path: Path relative to project root.

        Returns:
            Loaded DataFrame.

        Raises:
            FileNotFoundError: If the file does not exist.
            RuntimeError: On CSV parse failure.
        """
        path = _abs(rel_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        try:
            df = pd.read_csv(path)
            logger.info("Loaded DataFrame | rows=%d | path=%s", len(df), path)
            return df
        except Exception as exc:
            raise RuntimeError(f"Failed to read CSV '{path}': {exc}") from exc

    # ── JSON ──────────────────────────────────────────────────────────────────

    @staticmethod
    def save_json(data: dict, rel_path: str) -> str:
        """Atomically save a dict as JSON."""
        path = _abs(rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        dir_ = os.path.dirname(path)
        try:
            fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            os.replace(tmp, path)
        except OSError as exc:
            logger.error("Failed to save JSON '%s': %s", path, exc)
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        logger.info("Saved JSON | path=%s", path)
        return path

    @staticmethod
    def load_json(rel_path: str) -> dict:
        """Load a JSON file as a dict."""
        path = _abs(rel_path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ── Text / Markdown ───────────────────────────────────────────────────────

    @staticmethod
    def save_text(content: str, rel_path: str) -> str:
        """Save a plain-text or Markdown string to a file."""
        path = _abs(rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Saved text file | path=%s", path)
        return path

    @staticmethod
    def load_text(rel_path: str) -> str:
        """Read a text file and return its content."""
        path = _abs(rel_path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def timestamp_suffix() -> str:
        """Return a UTC timestamp string safe for filenames."""
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
