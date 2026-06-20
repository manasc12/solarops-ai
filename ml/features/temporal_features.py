"""Temporal feature engineering.

Pure, reusable transforms that derive cyclical time features from timestamps.
Identical code path is used at training and inference time for reproducibility.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TEMPORAL_FEATURES = [
    "hour_sin",
    "hour_cos",
    "doy_sin",
    "doy_cos",
    "is_daylight",
]


def add_temporal_features(df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
    """Append cyclical hour/day-of-year features and a daylight flag."""
    out = df.copy()
    ts = pd.to_datetime(out[timestamp_col], utc=True)
    hour = ts.dt.hour + ts.dt.minute / 60.0
    doy = ts.dt.dayofyear
    out["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
    out["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
    out["doy_sin"] = np.sin(2 * np.pi * doy / 365.0)
    out["doy_cos"] = np.cos(2 * np.pi * doy / 365.0)
    out["is_daylight"] = ((hour >= 6) & (hour <= 18)).astype(int)
    return out
