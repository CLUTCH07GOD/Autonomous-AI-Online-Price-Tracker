from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def _clip(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def detect_fake_discount(
    current_price: float,
    mrp: float | None,
    historical_average: float | None,
    historical_min: float | None = None,
    historical_max: float | None = None,
    anomaly_score: float = 0.0,
) -> dict:
    if not mrp or not historical_average or current_price <= 0:
        return {"is_fake_discount": False, "confidence": 0.35, "reason": "insufficient_history"}

    advertised_discount = _clip((mrp - current_price) / mrp)
    real_discount = _clip((historical_average - current_price) / historical_average)
    mrp_inflation = _clip((mrp - historical_average) / historical_average)
    fake_mrp = mrp_inflation > 0.18 and advertised_discount - real_discount > 0.15
    spike = bool(historical_max and mrp > historical_max * 1.15)
    suspicious = fake_mrp or spike or (advertised_discount > 0.30 and real_discount < 0.04) or anomaly_score > 0.7
    confidence = _clip(0.36 + mrp_inflation * 0.55 + (advertised_discount - real_discount) * 0.45 + anomaly_score * 0.25)
    return {
        "is_fake_discount": suspicious,
        "confidence": round(confidence, 4),
        "advertised_discount_pct": round(advertised_discount * 100, 2),
        "real_discount_pct": round(real_discount * 100, 2),
        "inflated_mrp_score": round(_clip(mrp_inflation), 4),
        "suspicious_spike": spike,
        "fake_mrp_detected": fake_mrp,
        "anomaly_score": round(_clip(anomaly_score), 4),
    }


def anomaly_scores(history: pd.DataFrame) -> pd.Series:
    if len(history) < 8:
        return pd.Series([0.0] * len(history), index=history.index)
    frame = history.copy()
    frame["price"] = frame["price"].astype(float)
    frame["rolling_mean"] = frame["price"].rolling(5, min_periods=1).mean()
    frame["pct_change"] = frame["price"].pct_change().replace([np.inf, -np.inf], 0).fillna(0)
    model = IsolationForest(contamination=min(0.18, max(0.05, 2 / len(frame))), random_state=42)
    labels = model.fit_predict(frame[["price", "rolling_mean", "pct_change"]])
    decision = model.decision_function(frame[["price", "rolling_mean", "pct_change"]])
    normalized = 1 - (decision - decision.min()) / (decision.max() - decision.min() or 1)
    return pd.Series([float(score) if label == -1 else float(score) * 0.35 for label, score in zip(labels, normalized)], index=history.index)
