"""Forecast model metadata accessor for the agent layer."""

from __future__ import annotations

import json
from pathlib import Path

from backend.app.core.config import settings
from ml.training.train_forecasting import META_FILENAME


def model_metadata() -> dict:
    path = Path(settings.model_dir) / META_FILENAME
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"model_version": "v1", "backend": "unknown"}
