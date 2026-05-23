from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split

from app.ml.preprocess import build_features

try:
    from xgboost import XGBRegressor
except Exception:  # optional at runtime for lightweight dev installs
    XGBRegressor = None

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(exist_ok=True)


FEATURE_COLUMNS = ["day_index", "hour", "day_of_week", "month", "rolling_3", "rolling_7", "discount_pct", "volatility_7"]


def _evaluate(y_true: pd.Series, predictions: Any) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, predictions)),
        "rmse": float(mean_squared_error(y_true, predictions, squared=False)),
        "r2": float(r2_score(y_true, predictions)) if len(y_true) > 1 else 0.0,
    }


def train_price_model(history: pd.DataFrame, model_name: str = "random_forest") -> dict:
    frame = build_features(history)
    features = frame[FEATURE_COLUMNS]
    target = frame["price"]
    if len(frame) < 8:
        model = LinearRegression()
        model.fit(features, target)
        metrics = {"mae": 0.0, "rmse": 0.0, "r2": 0.0}
    else:
        x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.25, shuffle=False)
        if model_name == "xgboost" and XGBRegressor is not None:
            model = XGBRegressor(n_estimators=160, max_depth=4, learning_rate=0.06, random_state=42)
        elif model_name == "linear_regression":
            model = LinearRegression()
        else:
            model = GridSearchCV(
                RandomForestRegressor(random_state=42),
                {"n_estimators": [80, 160], "max_depth": [4, 8, None]},
                cv=3,
                scoring="neg_mean_absolute_error",
            )
        model.fit(x_train, y_train)
        fitted = model.best_estimator_ if hasattr(model, "best_estimator_") else model
        metrics = _evaluate(y_test, fitted.predict(x_test))
        model = fitted
    path = MODEL_DIR / f"price_{model_name}.joblib"
    joblib.dump({"model": model, "features": FEATURE_COLUMNS, "metrics": metrics}, path)
    return {"model": str(path), "model_name": model_name, "samples": len(frame), **metrics}


def train_lstm_model(history: pd.DataFrame) -> dict:
    try:
        from tensorflow import keras
    except Exception:
        return {"model_name": "lstm", "status": "skipped", "reason": "tensorflow_not_installed"}

    prices = history.sort_values("captured_at")["price"].astype(float).to_numpy()
    if len(prices) < 16:
        return {"model_name": "lstm", "status": "skipped", "reason": "not_enough_sequence_history"}

    minimum = float(np.min(prices))
    scale = float(np.max(prices) - minimum)
    if scale <= 0:
        return {"model_name": "lstm", "status": "skipped", "reason": "flat_price_history"}

    normalized = (prices - minimum) / scale
    window = 10
    x_rows, y_rows = [], []
    for index in range(window, len(normalized)):
        x_rows.append(normalized[index - window : index])
        y_rows.append(normalized[index])
    x = np.array(x_rows).reshape(-1, window, 1)
    y = np.array(y_rows)

    model = keras.Sequential(
        [
            keras.layers.Input(shape=(window, 1)),
            keras.layers.LSTM(32, activation="tanh"),
            keras.layers.Dense(16, activation="relu"),
            keras.layers.Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mse")
    model.fit(x, y, epochs=20, batch_size=8, verbose=0)
    path = MODEL_DIR / "price_lstm.keras"
    model.save(path)
    return {"model": str(path), "model_name": "lstm", "status": "trained", "samples": len(prices)}


def train_all_models(history: pd.DataFrame) -> dict:
    candidates = ["linear_regression", "random_forest", "xgboost"]
    results = [train_price_model(history, name) for name in candidates if name != "xgboost" or XGBRegressor is not None]
    lstm = train_lstm_model(history)
    best = min(results, key=lambda item: item["mae"])
    return {"best": best, "candidates": results, "lstm": lstm}
