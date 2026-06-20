"""Thin wrapper exposing the anomaly detector to the agent layer."""

from __future__ import annotations

from ml.inference.anomaly_pipeline import get_anomaly_pipeline


def score(vector: list[float]) -> float:
    return get_anomaly_pipeline().score(vector)
