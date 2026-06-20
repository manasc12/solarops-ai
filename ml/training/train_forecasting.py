"""Forecasting model training pipeline.

Builds a reproducible synthetic training set from the farm registry, trains a
LightGBM regressor (falling back to scikit-learn GradientBoosting if LightGBM
is unavailable), and persists a versioned artifact + metadata.

Run standalone:
    python -m ml.training.train_forecasting
"""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import FarmRepository
from backend.app.services.synthetic import (
    generate_energy_series,
    generate_weather_series,
)
from ml.features import FEATURE_COLUMNS, build_feature_frame, feature_matrix

logger = get_logger("ml.training.forecasting")

MODEL_VERSION = "v1"
MODEL_FILENAME = "forecast_model.pkl"
META_FILENAME = "forecast_model.meta.json"


@dataclass
class TrainingResult:
    model_version: str
    backend: str
    n_samples: int
    artifact_path: str


def _build_dataset(history_hours: int = 24 * 30) -> pd.DataFrame:
    """Construct a labelled (features -> energy_kwh) dataset across all farms."""
    farms = FarmRepository().list()
    frames: list[pd.DataFrame] = []
    for farm in farms:
        weather = generate_weather_series(farm, hours=history_hours)
        energy = generate_energy_series(farm, weather)
        records = [w.model_dump() for w in weather]
        feats = build_feature_frame(records)
        feats["energy_kwh"] = [e.energy_kwh for e in energy]
        frames.append(feats)
    return pd.concat(frames, ignore_index=True)


def _make_model() -> tuple[Any, str]:
    try:
        from lightgbm import LGBMRegressor

        model = LGBMRegressor(
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.9,
            verbose=-1,
        )
        return model, "lightgbm"
    except Exception:  # pragma: no cover - fallback path
        from sklearn.ensemble import GradientBoostingRegressor

        log_event(logger, "lightgbm_unavailable_fallback", backend="gradient_boosting")
        return GradientBoostingRegressor(n_estimators=300, learning_rate=0.05), "gradient_boosting"


def train(history_hours: int = 24 * 30) -> TrainingResult:
    dataset = _build_dataset(history_hours=history_hours)
    x = feature_matrix(dataset)
    y = dataset["energy_kwh"]

    model, backend = _make_model()
    model.fit(x, y)

    model_dir = Path(settings.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = model_dir / MODEL_FILENAME
    with artifact_path.open("wb") as fh:
        pickle.dump({"model": model, "features": FEATURE_COLUMNS}, fh)

    meta = {
        "model_version": MODEL_VERSION,
        "backend": backend,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(dataset)),
        "features": FEATURE_COLUMNS,
    }
    (model_dir / META_FILENAME).write_text(json.dumps(meta, indent=2), encoding="utf-8")

    log_event(logger, "forecast_model_trained", backend=backend, n_samples=len(dataset))
    return TrainingResult(MODEL_VERSION, backend, len(dataset), str(artifact_path))


if __name__ == "__main__":
    result = train()
    print(f"Trained {result.backend} model on {result.n_samples} samples -> {result.artifact_path}")
