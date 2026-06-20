"""Anomaly detector training (IsolationForest on normal behaviour).

Generates fault-free synthetic operations across all farms, builds anomaly
feature vectors comparing model forecast vs actual, and fits an IsolationForest
that learns the normal deviation manifold. Faults later appear as outliers.

Run standalone:
    python -m ml.training.train_anomaly
"""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.logging import get_logger, log_event
from backend.app.db.repository import FarmRepository
from backend.app.services.synthetic import (
    expected_energy_kwh,
    generate_energy_series,
    generate_weather_series,
)
from ml.features.anomaly_features import ANOMALY_FEATURES, build_anomaly_vector

logger = get_logger("ml.training.anomaly")

MODEL_FILENAME = "anomaly_model.pkl"
META_FILENAME = "anomaly_model.meta.json"


@dataclass
class AnomalyTrainingResult:
    n_samples: int
    artifact_path: str


def _build_normal_vectors(history_hours: int = 24 * 20) -> list[list[float]]:
    farms = FarmRepository().list()
    vectors: list[list[float]] = []
    for farm in farms:
        weather = generate_weather_series(farm, hours=history_hours)
        actuals = generate_energy_series(farm, weather)  # no faults => normal
        for actual, wx in zip(actuals, weather):
            # Inference evaluates at the daytime peak hour, so the normal manifold
            # must reflect production hours. Night-time zero-output points would
            # otherwise dominate and distort the deviation distribution.
            if wx.irradiance_wm2 < 50.0:
                continue
            predicted = expected_energy_kwh(farm, wx)
            vectors.append(build_anomaly_vector(predicted, actual, wx, farm.capacity_kwp))
    return vectors


def train(history_hours: int = 24 * 20) -> AnomalyTrainingResult:
    from sklearn.ensemble import IsolationForest

    vectors = _build_normal_vectors(history_hours=history_hours)
    model = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
    model.fit(vectors)

    model_dir = Path(settings.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = model_dir / MODEL_FILENAME
    with artifact_path.open("wb") as fh:
        pickle.dump({"model": model, "features": ANOMALY_FEATURES}, fh)

    meta = {
        "method": "IsolationForest",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": len(vectors),
        "features": ANOMALY_FEATURES,
    }
    (model_dir / META_FILENAME).write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log_event(logger, "anomaly_model_trained", n_samples=len(vectors))
    return AnomalyTrainingResult(len(vectors), str(artifact_path))


if __name__ == "__main__":
    result = train()
    print(f"Trained IsolationForest on {result.n_samples} samples -> {result.artifact_path}")
