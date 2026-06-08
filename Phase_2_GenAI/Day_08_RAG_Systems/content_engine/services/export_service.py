"""
Export service module.
Converts generated content or history records to TXT, JSON, and CSV formats.
"""

import csv
import io
import json
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
        header = f"Platform: {platform.upper()}\nTopic: {topic}\n{'─' * 50}\n\n"
        text = header + content
        logger.info("TXT export | platform=%s", platform)
        return text.encode("utf-8")

    @staticmethod
    def export_json(record: dict) -> bytes:
        """
        Export a single history record as a JSON file.

        Args:
            record: Dictionary containing all generation metadata.

        Returns:
            UTF-8 encoded JSON bytes.
        """
        logger.info("JSON export | platform=%s", record.get("platform"))
        return json.dumps(record, indent=2, ensure_ascii=False).encode("utf-8")

    @staticmethod
    def export_csv(history: list[dict]) -> bytes:
        """
        Export the full history list as a CSV file.

        Args:
            history: List of history record dicts.

        Returns:
            UTF-8 encoded CSV bytes.
        """
        if not history:
            logger.warning("CSV export called with empty history.")
            return b"timestamp,platform,topic,tone,length,content\n"

        buf = io.StringIO()
        fieldnames = ["timestamp", "platform", "topic", "tone", "length", "content"]
        writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(history)
        logger.info("CSV export | %d records", len(history))
        return buf.getvalue().encode("utf-8")
