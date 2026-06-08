"""
Analytics Agent — KPI calculation and LLM-powered business insights.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from services.llm_service     import GroqService
from services.storage_service import StorageService
from utils.logger              import get_logger

logger = get_logger(__name__)

_KPI_PATH = "reports/kpis.json"


class AnalyticsAgent:
    """Computes KPIs from a processed DataFrame and generates LLM insights."""

    def __init__(self, llm: GroqService, storage: StorageService) -> None:
        self._llm     = llm
        self._storage = storage

    def calculate_kpis(self, df: pd.DataFrame, cleaning_report: dict | None = None) -> dict:
        """
        Calculate domain-agnostic KPIs from the DataFrame.

        Args:
            df:              Processed DataFrame (may be scaled/encoded).
            cleaning_report: Optional cleaning summary dict.

        Returns:
            KPI dictionary.
        """
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        obj_cols = df.select_dtypes(include="object").columns.tolist()

        kpis: dict = {
            "total_records":      len(df),
            "total_columns":      len(df.columns),
            "numeric_columns":    len(num_cols),
            "categorical_columns": len(obj_cols),
            "missing_values":     int(df.isna().sum().sum()),
            "duplicate_rows":     int(df.duplicated().sum()),
            "memory_usage_kb":    round(df.memory_usage(deep=True).sum() / 1024, 2),
        }

        # Numeric averages (first 8 columns)
        for col in num_cols[:8]:
            kpis[f"avg_{col}"] = round(float(df[col].mean()), 4)

        # Category distributions (first 3 categorical)
        for col in obj_cols[:3]:
            kpis[f"dist_{col}"] = df[col].value_counts(normalize=True).head(5).round(3).to_dict()

        # Churn-specific KPI
        churn_col = next((c for c in df.columns if "churn" in c.lower()), None)
        if churn_col:
            try:
                kpis["churn_rate"] = round(float(pd.to_numeric(df[churn_col], errors="coerce").mean()), 4)
            except Exception:
                pass

        # Revenue-specific KPI
        rev_col = next((c for c in df.columns if "revenue" in c.lower() or "charge" in c.lower()), None)
        if rev_col:
            try:
                kpis["total_revenue"]   = round(float(df[rev_col].sum()),  2)
                kpis["average_revenue"] = round(float(df[rev_col].mean()), 2)
            except Exception:
                pass

        # Cleaning summary passthrough
        if cleaning_report:
            kpis["cleaning_summary"] = {
                "duplicates_removed": cleaning_report.get("duplicates_removed", 0),
                "missing_filled":     len(cleaning_report.get("missing_filled", {})),
            }

        self._storage.save_json(kpis, _KPI_PATH)
        logger.info("KPIs calculated and saved | total_records=%d", kpis["total_records"])
        return kpis

    def generate_insights(self, kpis: dict, description: str) -> str:
        """
        Use Groq to generate business insights from the KPIs.

        Args:
            kpis:        Computed KPI dictionary.
            description: Original user dataset description.

        Returns:
            Markdown-formatted insight string.
        """
        logger.info("Generating LLM insights")
        try:
            return self._llm.generate_insights(kpis, description)
        except RuntimeError as exc:
            logger.error("Insight generation failed: %s", exc)
            return f"*Insights unavailable: {exc}*"
