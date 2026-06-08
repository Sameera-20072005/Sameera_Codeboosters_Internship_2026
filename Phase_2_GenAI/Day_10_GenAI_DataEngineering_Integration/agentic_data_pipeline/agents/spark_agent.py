"""
Spark Agent — distributed processing with graceful Pandas fallback.

PySpark requires Java 8/11/17 to be installed and on PATH.
If Spark cannot be initialised, the agent transparently falls back
to an equivalent Pandas-based computation so the rest of the
pipeline continues uninterrupted.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from services.storage_service import StorageService
from utils.logger              import get_logger

logger = get_logger(__name__)

_SPARK_OUTPUT_DIR = "data/spark_outputs"


@dataclass
class SparkMetrics:
    """Summary statistics produced by SparkAgent."""
    engine:           str            = "pandas"   # "spark" or "pandas"
    row_count:        int            = 0
    col_count:        int            = 0
    numeric_summary:  dict           = field(default_factory=dict)
    column_nulls:     dict           = field(default_factory=dict)
    top_categories:   dict           = field(default_factory=dict)
    aggregations:     dict           = field(default_factory=dict)

    def to_dict(self) -> dict:
        return self.__dict__


class SparkAgent:
    """
    Performs distributed aggregations using PySpark when available,
    falling back to an equivalent Pandas implementation otherwise.
    """

    def __init__(self, storage: StorageService) -> None:
        self._storage  = storage
        self._spark: Any = None
        self._use_spark  = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def initialize_spark(self) -> bool:
        """
        Attempt to create a SparkSession.

        Returns:
            True if Spark is available and initialised, False otherwise.
        """
        try:
            from pyspark.sql import SparkSession  # type: ignore
            self._spark = (
                SparkSession.builder
                .appName("AgenticDataPipeline")
                .master("local[*]")
                .config("spark.sql.shuffle.partitions", "4")
                .config("spark.driver.memory", "1g")
                .config("spark.sql.execution.arrow.pyspark.enabled", "false")
                .getOrCreate()
            )
            self._spark.sparkContext.setLogLevel("ERROR")
            self._use_spark = True
            logger.info("SparkSession initialised successfully.")
            return True
        except Exception as exc:
            logger.warning("PySpark unavailable (%s) — using Pandas fallback.", exc)
            self._use_spark = False
            return False

    def stop(self) -> None:
        """Stop the SparkSession if active."""
        if self._use_spark and self._spark:
            try:
                self._spark.stop()
                logger.info("SparkSession stopped.")
            except Exception:
                pass

    # ── Public ────────────────────────────────────────────────────────────────

    def process_dataset(self, df: pd.DataFrame) -> SparkMetrics:
        """
        Run distributed (or Pandas-fallback) aggregations on the DataFrame.

        Args:
            df: Transformed DataFrame.

        Returns:
            SparkMetrics dataclass.
        """
        if self._use_spark:
            return self._process_with_spark(df)
        return self._process_with_pandas(df)

    def generate_spark_metrics(self, metrics: SparkMetrics) -> dict:
        """Return metrics as a plain dict for storage / reporting."""
        return metrics.to_dict()

    def save_metrics(self, metrics: SparkMetrics) -> str:
        """Persist Spark/Pandas metrics to JSON."""
        ts  = StorageService.timestamp_suffix()
        rel = f"{_SPARK_OUTPUT_DIR}/spark_metrics_{ts}.json"
        self._storage.save_json(metrics.to_dict(), rel)
        logger.info("Spark metrics saved | engine=%s | path=%s", metrics.engine, rel)
        return rel

    # ── Spark processing ──────────────────────────────────────────────────────

    def _process_with_spark(self, df: pd.DataFrame) -> SparkMetrics:
        """Run aggregations using PySpark."""
        from pyspark.sql import functions as F  # type: ignore
        logger.info("Processing with Spark | rows=%d", len(df))

        sdf = self._spark.createDataFrame(df)
        metrics = SparkMetrics(engine="spark", row_count=sdf.count(), col_count=len(sdf.columns))

        # Null counts per column
        null_exprs  = [F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in sdf.columns]
        null_row    = sdf.select(null_exprs).collect()[0]
        metrics.column_nulls = null_row.asDict()

        # Numeric summary: mean, stddev, min, max
        num_cols = [f.name for f in sdf.schema.fields
                    if str(f.dataType) in ("DoubleType()", "FloatType()", "IntegerType()", "LongType()")]
        summary: dict = {}
        for col in num_cols[:10]:   # cap to 10 columns
            row = sdf.select(
                F.mean(col).alias("mean"),
                F.stddev(col).alias("std"),
                F.min(col).alias("min"),
                F.max(col).alias("max"),
            ).collect()[0]
            summary[col] = {k: (round(v, 4) if v is not None else None) for k, v in row.asDict().items()}
        metrics.numeric_summary = summary

        # Top categories for string columns
        str_cols = [f.name for f in sdf.schema.fields if str(f.dataType) == "StringType()"]
        top_cats: dict = {}
        for col in str_cols[:5]:
            rows = (sdf.groupBy(col).count().orderBy(F.desc("count")).limit(5).collect())
            top_cats[col] = {r[col]: r["count"] for r in rows}
        metrics.top_categories = top_cats

        # Row-count aggregation by groups (first string column if present)
        if str_cols:
            agg_col = str_cols[0]
            agg_rows = sdf.groupBy(agg_col).count().orderBy(F.desc("count")).limit(10).collect()
            metrics.aggregations = {agg_col: {r[agg_col]: r["count"] for r in agg_rows}}

        return metrics

    # ── Pandas fallback ───────────────────────────────────────────────────────

    def _process_with_pandas(self, df: pd.DataFrame) -> SparkMetrics:
        """Equivalent aggregations using Pandas (Spark not available)."""
        logger.info("Processing with Pandas fallback | rows=%d", len(df))
        metrics = SparkMetrics(engine="pandas", row_count=len(df), col_count=len(df.columns))

        # Null counts
        metrics.column_nulls = {c: int(df[c].isna().sum()) for c in df.columns}

        # Numeric summary
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        summary: dict = {}
        for col in num_cols[:10]:
            summary[col] = {
                "mean": round(float(df[col].mean()), 4),
                "std":  round(float(df[col].std()),  4),
                "min":  round(float(df[col].min()),  4),
                "max":  round(float(df[col].max()),  4),
            }
        metrics.numeric_summary = summary

        # Top categories for object columns
        obj_cols = df.select_dtypes(include="object").columns.tolist()
        top_cats: dict = {}
        for col in obj_cols[:5]:
            top_cats[col] = df[col].value_counts().head(5).to_dict()
        metrics.top_categories = top_cats

        # Aggregation
        if obj_cols:
            agg_col = obj_cols[0]
            metrics.aggregations = {agg_col: df[agg_col].value_counts().head(10).to_dict()}

        return metrics
