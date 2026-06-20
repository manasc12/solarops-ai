"""Reusable feature pipeline shared by training and inference."""

from __future__ import annotations

import pandas as pd

from ml.features.temporal_features import TEMPORAL_FEATURES, add_temporal_features
from ml.features.weather_features import WEATHER_FEATURES, add_weather_features

FEATURE_COLUMNS = WEATHER_FEATURES + TEMPORAL_FEATURES


def build_feature_frame(weather_records: list[dict]) -> pd.DataFrame:
    """Turn a list of weather dicts into a feature matrix.

    The same function is used for training (with a ``energy_kwh`` target column
    present) and inference (without it), guaranteeing identical features.
    """
    df = pd.DataFrame(weather_records)
    df = df.sort_values("timestamp").reset_index(drop=True)
    df = add_weather_features(df)
    df = add_temporal_features(df)
    return df


def feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    return df[FEATURE_COLUMNS]


__all__ = ["FEATURE_COLUMNS", "build_feature_frame", "feature_matrix"]
