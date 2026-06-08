"""
Transformation Agent — feature engineering, encoding, and scaling.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from services.storage_service import StorageService
from utils.logger              import get_logger

logger = get_logger(__name__)

_TRANSFORMED_DIR = "data/transformed"

# Columns likely to benefit from log-transform (revenue / monetary)
_LOG_KEYWORDS = {"revenue", "income", "spend", "amount", "charge", "value", "salary", "cost", "price"}


@dataclass
class TransformationReport:
    """Tracks what transformations were applied."""
    engineered_features: list[str] = field(default_factory=list)
    encoded_columns:     list[str] = field(default_factory=list)
    scaled_columns:      list[str] = field(default_factory=list)
    encoding_maps:       dict      = field(default_factory=dict)

    def to_dict(self) -> dict:
        return self.__dict__


class TransformationAgent:
    """Applies feature engineering, categorical encoding, and numeric scaling."""

    def __init__(self, storage: StorageService) -> None:
        self._storage = storage
        self._label_encoders: dict[str, LabelEncoder] = {}
        self._scaler: StandardScaler | None = None

    def engineer_features(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        """
        Add derived features based on existing numeric columns.

        Args:
            df: Cleaned DataFrame.

        Returns:
            Tuple of (DataFrame with new columns, list of added column names).
        """
        df      = df.copy()
        added: list[str] = []
        num_cols = df.select_dtypes(include=np.number).columns.tolist()

        # Log-transform monetary columns
        for col in num_cols:
            if any(kw in col.lower() for kw in _LOG_KEYWORDS):
                new_col = f"log_{col}"
                df[new_col] = np.log1p(df[col].clip(lower=0))
                added.append(new_col)

        # CLV proxy: if monthly_charges and tenure both exist
        if "monthly_charges" in df.columns and "tenure" in df.columns:
            df["customer_lifetime_value"] = df["monthly_charges"] * df["tenure"]
            added.append("customer_lifetime_value")

        # Annual revenue proxy
        if "monthly_charges" in df.columns and "annual_revenue" not in df.columns:
            df["annual_revenue"] = df["monthly_charges"] * 12
            added.append("annual_revenue")

        # Interaction: tenure x monthly_charges normalised ratio
        if "tenure" in df.columns and "monthly_charges" in df.columns:
            max_tenure = df["tenure"].max()
            if max_tenure and max_tenure > 0:
                df["tenure_charge_ratio"] = df["tenure"] / max_tenure * df["monthly_charges"]
                added.append("tenure_charge_ratio")

        logger.info("Feature engineering: added %d features — %s", len(added), added)
        return df, added

    def encode_features(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        Label-encode low-cardinality categorical columns and one-hot encode others.

        Args:
            df: DataFrame after feature engineering.

        Returns:
            Tuple of (encoded DataFrame, mapping dict).
        """
        df     = df.copy()
        maps   = {}
        object_cols = df.select_dtypes(include="object").columns.tolist()

        for col in object_cols:
            n_unique = df[col].nunique()
            if n_unique <= 10:
                # LabelEncoder for low-cardinality
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self._label_encoders[col] = le
                maps[col] = {
                    "type":    "label",
                    "classes": le.classes_.tolist(),
                }
                logger.debug("LabelEncoded '%s' | classes=%d", col, n_unique)
            elif n_unique <= 30:
                # OneHotEncoder via pandas get_dummies
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True).astype(int)
                df      = pd.concat([df.drop(columns=[col]), dummies], axis=1)
                maps[col] = {
                    "type":    "onehot",
                    "columns": dummies.columns.tolist(),
                }
                logger.debug("OneHotEncoded '%s' | columns=%d", col, len(dummies.columns))
            else:
                # High-cardinality: drop column
                df    = df.drop(columns=[col])
                maps[col] = {"type": "dropped", "reason": "high_cardinality"}
                logger.debug("Dropped '%s' (high cardinality=%d)", col, n_unique)

        logger.info("Encoding complete | encoded=%d columns", len(maps))
        return df, maps

    def scale_features(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        """
        Apply StandardScaler to all remaining numeric columns.

        Args:
            df: Encoded DataFrame.

        Returns:
            Tuple of (scaled DataFrame, list of scaled column names).
        """
        df       = df.copy()
        num_cols = df.select_dtypes(include=np.number).columns.tolist()

        if not num_cols:
            logger.warning("No numeric columns to scale.")
            return df, []

        scaler       = StandardScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
        self._scaler = scaler
        logger.info("Scaling complete | scaled=%d columns", len(num_cols))
        return df, num_cols

    def save_transformed(self, df: pd.DataFrame, name: str = "transformed") -> str:
        """Save the transformed DataFrame and return its relative path."""
        ts  = StorageService.timestamp_suffix()
        rel = f"{_TRANSFORMED_DIR}/{name}_{ts}.csv"
        self._storage.save_dataframe(df, rel)
        logger.info("Transformed dataset saved | path=%s", rel)
        return rel
