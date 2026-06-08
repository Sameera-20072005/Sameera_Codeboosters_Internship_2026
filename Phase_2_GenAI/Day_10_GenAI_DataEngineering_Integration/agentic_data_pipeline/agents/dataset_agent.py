"""
Dataset Agent — generates a synthetic structured CSV dataset using Groq LLM.
"""
from __future__ import annotations

import io
import pandas as pd
from services.llm_service     import GroqService
from services.storage_service import StorageService
from utils.logger              import get_logger

logger = get_logger(__name__)

_RAW_DIR = "data/raw"


class DatasetAgent:
    """Generates synthetic datasets from natural language descriptions."""

    def __init__(self, llm: GroqService, storage: StorageService) -> None:
        self._llm     = llm
        self._storage = storage

    def generate_dataset(
        self,
        description: str,
        record_count: int = 200,
        domain: str = "general",
    ) -> pd.DataFrame:
        """
        Generate a structured synthetic dataset via LLM.

        Args:
            description:  Natural language dataset request.
            record_count: Number of data rows to generate (capped at 500 for LLM limits).
            domain:       Domain hint (telecom, banking, retail, etc.).

        Returns:
            Generated DataFrame.

        Raises:
            RuntimeError: On LLM or CSV parsing failure.
        """
        safe_count = min(max(record_count, 10), 500)
        enriched   = f"Domain: {domain}. {description}"

        logger.info("DatasetAgent generating | domain=%s | records=%d", domain, safe_count)
        csv_text = self._llm.generate_dataset(enriched, safe_count)
        df       = self._parse_csv(csv_text)

        logger.info("Dataset generated | shape=%s", df.shape)
        return df

    def save_dataset(self, df: pd.DataFrame, name: str = "dataset") -> str:
        """
        Persist the raw dataset to disk.

        Args:
            df:   DataFrame to save.
            name: Base filename (without extension).

        Returns:
            Relative path of saved file.
        """
        ts      = StorageService.timestamp_suffix()
        rel     = f"{_RAW_DIR}/{name}_{ts}.csv"
        self._storage.save_dataframe(df, rel)
        logger.info("Raw dataset saved | path=%s", rel)
        return rel

    # ── Private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_csv(csv_text: str) -> pd.DataFrame:
        """
        Parse raw CSV text into a DataFrame, with fallback cleaning.

        Args:
            csv_text: Raw CSV string from the LLM.

        Returns:
            Parsed DataFrame.

        Raises:
            RuntimeError: If the CSV cannot be parsed at all.
        """
        text = csv_text.strip()
        # Drop any lines that look like prose (don't contain commas)
        lines = [l for l in text.splitlines() if "," in l]
        if not lines:
            raise RuntimeError("LLM did not return valid CSV — no comma-separated lines found.")
        cleaned = "\n".join(lines)
        try:
            df = pd.read_csv(io.StringIO(cleaned))
            if df.empty or len(df.columns) < 2:
                raise ValueError("Parsed DataFrame is empty or has fewer than 2 columns.")
            return df
        except Exception as exc:
            raise RuntimeError(f"CSV parsing failed: {exc}") from exc
