"""Thin wrapper exposing the forecast inference pipeline to the agent layer."""

from __future__ import annotations

from ml.inference.forecast_pipeline import get_forecast_pipeline


def predict_series(weather_records: list[dict]) -> list[float]:
    return get_forecast_pipeline().predict_series(weather_records)
