"""Forecast inference pipeline.

Loads the trained forecasting artifact (auto-training on first use if absent)
and produces hourly energy predictions for a weather series. Pure inference —
no training logic and no schema construction here.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from ml.features import build_feature_frame, feature_matrix
from ml.training.train_forecasting import MODEL_FILENAME, MODEL_VERSION

logger = get_logger("ml.inference.forecast")


class ForecastPipeline:
    def __init__(self) -> None:
        self._model: Any | None = None
        self._features: list[str] | None = None

    def _artifact_path(self) -> Path:
        return Path(settings.model_dir) / MODEL_FILENAME

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        path = self._artifact_path()
        if not path.exists():
            log_event(logger, "model_missing_autotrain")
            from ml.training.train_forecasting import train

            train()
        with path.open("rb") as fh:
            bundle = pickle.load(fh)
        self._model = bundle["model"]
        self._features = bundle["features"]

    def predict_series(self, weather_records: list[dict]) -> list[float]:
        """Predict hourly energy (kWh) for each weather record."""
        self._ensure_loaded()
        frame = build_feature_frame(weather_records)
        x = feature_matrix(frame)
        preds = np.asarray(self._model.predict(x), dtype=float)
        preds = np.clip(preds, a_min=0.0, a_max=None)
        return [round(float(p), 3) for p in preds]

    @property
    def model_version(self) -> str:
        return MODEL_VERSION


_pipeline: ForecastPipeline | None = None


def get_forecast_pipeline() -> ForecastPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = ForecastPipeline()
    return _pipeline
