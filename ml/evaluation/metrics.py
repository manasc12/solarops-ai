"""Forecast error metrics producing the canonical ForecastEvaluation schema."""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from backend.app.models.schemas import ForecastEvaluation


def compute_metrics(farm_id: str, y_true: list[float], y_pred: list[float]) -> ForecastEvaluation:
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    err = yp - yt
    mae = float(np.mean(np.abs(err))) if len(err) else 0.0
    rmse = float(np.sqrt(np.mean(err**2))) if len(err) else 0.0
    denom = np.where(np.abs(yt) < 1e-6, np.nan, yt)
    mape = float(np.nanmean(np.abs(err / denom)) * 100.0) if len(err) else 0.0
    bias = float(np.mean(err)) if len(err) else 0.0
    return ForecastEvaluation(
        farm_id=farm_id,
        timestamp=datetime.now(timezone.utc),
        mae=round(mae, 4),
        rmse=round(rmse, 4),
        mape=round(0.0 if np.isnan(mape) else mape, 4),
        bias=round(bias, 4),
    )
