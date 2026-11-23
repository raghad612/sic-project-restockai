
"""Shared evaluation metrics for T9 and later forecasting models."""

import numpy as np


def mae(y_true, y_pred):
    """Mean absolute error in the target's original units."""
    actual = np.asarray(y_true, dtype=np.float64)
    predicted = np.asarray(y_pred, dtype=np.float64)
    return float(np.mean(np.abs(actual - predicted)))


def wape(y_true, y_pred):
    """Weighted absolute percentage error, expressed as a percentage."""
    actual = np.asarray(y_true, dtype=np.float64)
    predicted = np.asarray(y_pred, dtype=np.float64)

    denominator = np.sum(actual)
    if denominator <= 0:
        return float("nan")

    return float(np.sum(np.abs(actual - predicted)) / denominator * 100)
