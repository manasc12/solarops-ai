"""Thin wrapper exposing forecast model training to the agent layer."""

from __future__ import annotations

from ml.training.train_forecasting import train


def train_model():
    return train()
