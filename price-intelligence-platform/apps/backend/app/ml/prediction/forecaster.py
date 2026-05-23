from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.preprocess import build_features
from app.models.prediction import MLPrediction
from app.models.price import PriceHistory
from app.models.product import Product

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


def _load_model() -> dict | None:
    for name in ["price_lstm.keras", "price_xgboost.joblib", "price_random_forest.joblib", "price_linear_regression.joblib"]:
        path = MODEL_DIR / name
        if path.exists():
            if path.suffix == ".keras":
                try:
                    from tensorflow import keras

                    return {"model": keras.models.load_model(path), "features": ["price"], "kind": "lstm"}
                except Exception:
                    continue
            return joblib.load(path)
    return None


def _history_frame(db: Session, product_id: int) -> pd.DataFrame:
    rows = db.execute(
        select(PriceHistory.price, PriceHistory.mrp, PriceHistory.captured_at)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.captured_at)
    ).all()
    if not rows:
        raise ValueError("No price history available for prediction")
    frame = pd.DataFrame(rows, columns=["price", "mrp", "captured_at"])
    frame["price"] = frame["price"].astype(float)
    frame["mrp"] = frame["mrp"].astype(float)
    return frame


def _volatility(prices: np.ndarray) -> float:
    if len(prices) < 2:
        return 0.0
    mean = float(np.mean(prices))
    return 0.0 if mean <= 0 else float(np.std(prices, ddof=1) / mean)


def _sequence_forecast(prices: np.ndarray, days: int) -> tuple[float, str]:
    window = prices[-min(14, len(prices)) :]
    if len(window) < 3:
        return float(window[-1]), "lstm_sequence_baseline"
    x = np.arange(len(window), dtype=float)
    slope, intercept = np.polyfit(x, window, 1)
    ewma = pd.Series(window).ewm(span=min(7, len(window)), adjust=False).mean().iloc[-1]
    seasonal = float(np.mean(np.diff(window[-min(7, len(window)) :]))) if len(window) > 3 else 0.0
    projected = (intercept + slope * (len(window) + days)) * 0.55 + ewma * 0.35 + (window[-1] + seasonal * days) * 0.10
    floor = max(min(prices) * 0.6, 1)
    ceiling = max(max(prices) * 1.6, floor)
    return float(np.clip(projected, floor, ceiling)), "lstm_sequence_baseline"


def _lstm_forecast(bundle: dict, prices: np.ndarray, days: int) -> float | None:
    if bundle.get("kind") != "lstm" or len(prices) < 10:
        return None
    minimum = float(np.min(prices))
    maximum = float(np.max(prices))
    scale = maximum - minimum
    if scale <= 0:
        return float(prices[-1])
    sequence = ((prices[-10:] - minimum) / scale).reshape(1, 10, 1)
    model = bundle["model"]
    predicted = None
    for _ in range(max(days, 1)):
        predicted = float(model.predict(sequence, verbose=0)[0][0])
        sequence = np.concatenate([sequence[:, 1:, :], np.array(predicted).reshape(1, 1, 1)], axis=1)
    return predicted * scale + minimum if predicted is not None else None


def forecast_price(db: Session, product_id: int, days: int = 7) -> MLPrediction:
    if days not in {7, 30}:
        days = 7 if days < 15 else 30

    history = _history_frame(db, product_id)
    frame = build_features(history)
    latest = frame.iloc[-1]
    bundle = _load_model()
    prices = history["price"].to_numpy(dtype=float)
    forecast_for = datetime.now(timezone.utc) + timedelta(days=days)

    predicted: float | None = _lstm_forecast(bundle or {}, prices, days)
    model_name = "lstm_price_forecaster" if predicted is not None else "lstm_sequence_baseline"

    if predicted is None and bundle and bundle.get("kind") != "lstm":
        model = bundle["model"]
        features = bundle["features"]
        feature_row = pd.DataFrame([{column: latest[column] for column in features}])
        feature_row["day_index"] = int(latest["day_index"]) + days
        feature_row["day_of_week"] = forecast_for.weekday()
        feature_row["month"] = forecast_for.month
        predicted = float(model.predict(feature_row[features])[0])
        model_name = type(model).__name__

    if predicted is None:
        predicted, model_name = _sequence_forecast(prices, days)

    product = db.get(Product, product_id)
    current = float(product.current_best_price or predicted)
    volatility = _volatility(prices)
    history_factor = min(len(prices) / 30, 1.0)
    horizon_penalty = 0.10 if days == 30 else 0.0
    confidence = max(0.25, min(0.92, 0.55 + history_factor * 0.25 - volatility * 1.4 - horizon_penalty))
    delta = (predicted - current) / current if current else 0
    signal = "HIGH CHANCE OF DROP" if delta < -0.05 else "BUY NOW" if delta > 0.03 else "WAIT"
    prediction = MLPrediction(
        product_id=product_id,
        model_name=model_name,
        predicted_price=Decimal(str(round(predicted, 2))),
        forecast_for=forecast_for,
        confidence=Decimal(str(round(confidence, 4))),
        signal=signal,
        meta={
            "horizon_days": days,
            "expected_delta_pct": round(delta * 100, 2),
            "volatility": round(volatility, 4),
            "history_points": int(len(prices)),
        },
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def forecast_standard_horizons(db: Session, product_id: int) -> list[MLPrediction]:
    return [forecast_price(db, product_id, days=7), forecast_price(db, product_id, days=30)]
