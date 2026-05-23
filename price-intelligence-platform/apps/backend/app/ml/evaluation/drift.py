from __future__ import annotations

import pandas as pd


def drift_score(baseline: pd.Series, recent: pd.Series) -> float:
    if baseline.empty or recent.empty:
        return 0.0
    base_mean = float(baseline.mean())
    if base_mean == 0:
        return 0.0
    return round(abs(float(recent.mean()) - base_mean) / base_mean, 4)
