"""Weather-derived feature engineering (reusable at train and inference time)."""

from __future__ import annotations

import pandas as pd

RAW_WEATHER_FEATURES = [
    "temperature_c",
    "cloud_cover_pct",
    "irradiance_wm2",
    "wind_speed_ms",
    "precipitation_prob",
    "uv_index",
]

DERIVED_WEATHER_FEATURES = [
    "clear_sky_factor",
    "temp_stress",
    "irradiance_lag1",
    "irradiance_roll3",
]

WEATHER_FEATURES = RAW_WEATHER_FEATURES + DERIVED_WEATHER_FEATURES


def add_weather_features(df: pd.DataFrame) -> pd.DataFrame:
    """Append derived and lagged weather features.

    Lag/rolling features are computed from irradiance, which is available at
    forecast time, keeping training and inference consistent.
    """
    out = df.copy()
    out["clear_sky_factor"] = 1.0 - (out["cloud_cover_pct"].clip(0, 100) / 100.0)
    out["temp_stress"] = (out["temperature_c"] - 25.0).clip(lower=0.0)
    out["irradiance_lag1"] = out["irradiance_wm2"].shift(1).fillna(out["irradiance_wm2"])
    out["irradiance_roll3"] = (
        out["irradiance_wm2"].rolling(window=3, min_periods=1).mean()
    )
    return out
