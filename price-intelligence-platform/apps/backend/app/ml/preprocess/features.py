from __future__ import annotations

import pandas as pd


def build_features(history: pd.DataFrame) -> pd.DataFrame:
    frame = history.sort_values("captured_at").copy()
    frame["captured_at"] = pd.to_datetime(frame["captured_at"])
    first = frame["captured_at"].min()
    frame["day_index"] = (frame["captured_at"] - first).dt.days
    frame["hour"] = frame["captured_at"].dt.hour
    frame["day_of_week"] = frame["captured_at"].dt.dayofweek
    frame["month"] = frame["captured_at"].dt.month
    frame["rolling_3"] = frame["price"].rolling(3, min_periods=1).mean()
    frame["rolling_7"] = frame["price"].rolling(7, min_periods=1).mean()
    frame["price_delta"] = frame["price"].diff().fillna(0)
    mrp = frame.get("mrp", frame["price"]).replace(0, pd.NA)
    frame["discount_pct"] = ((mrp - frame["price"]) / mrp).fillna(0)
    frame["volatility_7"] = frame["price"].rolling(7, min_periods=2).std().fillna(0)
    return frame


def competitor_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["effective_price"] = result["price"] + result.get("shipping_cost", 0)
    result["market_rank"] = result.groupby("product_id")["effective_price"].rank(method="dense")
    return result
