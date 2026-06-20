"""Anomaly inference pipeline.

Loads the IsolationForest artifact (auto-trains if missing) and converts its
raw score into a normalized 0..1 anomaly score.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from ml.training.train_anomaly import MODEL_FILENAME

logger = get_logger("ml.inference.anomaly")

# Steepness of the sigmoid mapping the (calibrated) decision function to 0..1.
_SCALE = 18.0


def _normalize_score(decision: float) -> float:
    """Map IsolationForest decision_function to a 0..1 anomaly score.

    ``decision_function`` is positive for inliers and negative for outliers
    (it equals ``score_samples - offset_``). Negating and squashing yields a
    calibrated anomaly score where outliers approach 1.0.
    """
    return float(1.0 / (1.0 + np.exp(_SCALE * decision)))


class AnomalyPipeline:
    def __init__(self) -> None:
        self._model = None

    def _artifact_path(self) -> Path:
        return Path(settings.model_dir) / MODEL_FILENAME

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        path = self._artifact_path()
        if not path.exists():
            log_event(logger, "anomaly_model_missing_autotrain")
            from ml.training.train_anomaly import train

            train()
        with path.open("rb") as fh:
            self._model = pickle.load(fh)["model"]

    def score(self, vector: list[float]) -> float:
        self._ensure_loaded()
        decision = float(self._model.decision_function([vector])[0])
        return round(_normalize_score(decision), 4)


_pipeline: AnomalyPipeline | None = None


def get_anomaly_pipeline() -> AnomalyPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = AnomalyPipeline()
    return _pipeline
