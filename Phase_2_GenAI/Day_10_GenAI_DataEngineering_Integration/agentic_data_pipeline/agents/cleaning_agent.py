"""
Cleaning Agent — deduplication, missing-value handling, column standardisation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import pandas as pd
from services.storage_service import StorageService
from utils.logger              import get_logger

logger = get_logger(__name__)

_CLEANED_DIR = "data/cleaned"


@dataclass
class CleaningReport:
    """Summary of all cleaning operations applied."""
    original_rows:   int = 0
    original_cols:   int = 0
    duplicates_removed: int = 0
    missing_filled:  dict = field(default_factory=dict)
    columns_renamed: list = field(default_factory=list)
    final_rows:      int = 0
    final_cols:      int = 0

    def to_dict(self) -> dict:
        return self.__dict__


class CleaningAgent:
    """Cleans raw DataFrames: deduplicates, imputes, standardises column names."""

    def __init__(self, storage: StorageService) -> None:
        self._storage = storage

    def clean_data(self, df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        """
        Apply all cleaning steps to the input DataFrame.

        Args:
            df: Raw DataFrame from DatasetAgent.

        Returns:
            Tuple of (cleaned DataFrame, CleaningReport).
        """
        report = CleaningReport(
            original_rows=len(df),
            original_cols=len(df.columns),
        )
        logger.info("CleaningAgent started | shape=%s", df.shape)

        df = df.copy()

        # ── 1. Standardise column names ───────────────────────────────────────
        original_cols  = list(df.columns)
        df.columns     = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(r"[\s\-/]+", "_", regex=True)
            .str.replace(r"[^\w]", "", regex=True)
        )
        report.columns_renamed = [
            f"{o} → {n}" for o, n in zip(original_cols, df.columns) if o != n
        ]

        # ── 2. Remove duplicate rows ──────────────────────────────────────────
        before = len(df)
        df     = df.drop_duplicates()
        report.duplicates_removed = before - len(df)

        # ── 3. Handle missing values ──────────────────────────────────────────
        missing_info: dict[str, int] = {}
        for col in df.columns:
            n_missing = int(df[col].isna().sum())
            if n_missing == 0:
                continue
            missing_info[col] = n_missing
            if df[col].dtype in ("float64", "int64", "float32", "int32"):
                df[col] = df[col].fillna(df[col].median())
            else:
                mode_vals = df[col].mode()
                fill_val  = mode_vals[0] if len(mode_vals) else "unknown"
                df[col]   = df[col].fillna(fill_val)
        report.missing_filled = missing_info

        # ── 4. Drop columns that are entirely null ────────────────────────────
        df = df.dropna(axis=1, how="all")

        # ── 5. Strip whitespace from string columns ───────────────────────────
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip()

        report.final_rows = len(df)
        report.final_cols = len(df.columns)
        logger.info(
            "Cleaning done | removed_dups=%d | missing_cols=%d | final_shape=%s",
            report.duplicates_removed, len(missing_info), df.shape,
        )
        return df, report

    def generate_cleaning_report(self, report: CleaningReport) -> dict:
        """Return the cleaning report as a plain dict."""
        return report.to_dict()

    def save_cleaned(self, df: pd.DataFrame, name: str = "cleaned") -> str:
        """Save cleaned DataFrame and return its relative path."""
        ts  = StorageService.timestamp_suffix()
        rel = f"{_CLEANED_DIR}/{name}_{ts}.csv"
        self._storage.save_dataframe(df, rel)
        logger.info("Cleaned dataset saved | path=%s", rel)
        return rel
