from __future__ import annotations

import math


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def popularity_score(rating: float | None, rating_count: int | None) -> float:
    rating_part = clamp((rating or 0) / 5)
    count_part = clamp(math.log1p(rating_count or 0) / math.log1p(10000))
    return round(rating_part * 0.62 + count_part * 0.38, 4)


def price_drop_score(current_price: float, historical_average: float, lowest_price: float | None = None) -> float:
    if historical_average <= 0:
        return 0.0
    below_average = clamp((historical_average - current_price) / historical_average)
    near_low = 0.0
    if lowest_price and current_price > 0:
        near_low = clamp(1 - ((current_price - lowest_price) / current_price))
    return round(below_average * 0.7 + near_low * 0.3, 4)


def recommendation_score(
    discount_pct: float,
    drop_probability: float,
    confidence: float,
    competitor_gap: float,
    rating_score: float = 0.0,
    volatility: float = 0.0,
    popularity: float = 0.0,
    price_drop: float = 0.0,
) -> float:
    stable_value = clamp(1 - volatility)
    score = (
        clamp(discount_pct) * 0.23
        + clamp(price_drop) * 0.22
        + clamp(rating_score) * 0.13
        + clamp(popularity) * 0.12
        + clamp(competitor_gap) * 0.11
        + clamp(confidence) * 0.09
        + stable_value * 0.06
        + clamp(1 - drop_probability) * 0.04
    )
    return round(clamp(score), 4)


def recommendation_label(score: float, drop_probability: float) -> str:
    if score >= 0.76 and drop_probability < 0.45:
        return "BEST DEAL TODAY"
    if drop_probability >= 0.65:
        return "HIGH CHANCE OF DROP"
    if score >= 0.55:
        return "BUY NOW"
    return "WAIT"
