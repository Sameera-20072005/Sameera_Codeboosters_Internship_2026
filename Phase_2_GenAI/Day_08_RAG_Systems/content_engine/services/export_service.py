"""
Export service module.
Converts generated content or history records to TXT, JSON, and CSV formats.
"""

import csv
import io
import json
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger(__name__)


class ExportService:
    """Handles exporting content to downloadable file formats."""

    @staticmethod
    def export_txt(content: str, platform: str, topic: str) -> bytes:
        """
        Export a single content piece as a plain-text file.

        Args:
            content: Generated content string.
            platform: Platform name for the file header.
            topic: Topic for the file header.

        Returns:
            UTF-8 encoded bytes ready for Streamlit download.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        header = (
            f"Platform : {platform.upper()}\n"
            f"Topic    : {topic}\n"
            f"Generated: {timestamp}\n"
            f"{'─' * 50}\n\n"
        )
        logger.info("TXT export | platform=%s", platform)
        return (header + content).encode("utf-8")

    @staticmethod
    def export_json(record: dict) -> bytes:
        """
        Export a single history record as a JSON file.
        Guards against being called with an empty record dict.

        Args:
            record: Dictionary containing all generation metadata.

        Returns:
            UTF-8 encoded JSON bytes.
        """
        if not record:
            logger.warning("export_json called with empty record.")
            return json.dumps({"error": "No content generated yet."}, indent=2).encode("utf-8")
        logger.info("JSON export | platform=%s", record.get("platform", "unknown"))
        return json.dumps(record, indent=2, ensure_ascii=False).encode("utf-8")

    @staticmethod
    def export_csv(history: list[dict]) -> bytes:
        """
        Export the full history list as a CSV file.

        Args:
            history: List of history record dicts.

        Returns:
            UTF-8 encoded CSV bytes (with BOM for Excel compatibility).
        """
        fieldnames = ["timestamp", "platform", "topic", "tone", "length", "content"]
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        if history:
            writer.writerows(history)
        logger.info("CSV export | %d records", len(history))
        # UTF-8 BOM so Excel opens it correctly without encoding issues
        return ("\ufeff" + buf.getvalue()).encode("utf-8")
