from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.intelligence import CompetitorPrice, DiscountAnalysis, TrendAnalysis
from app.models.price import PriceHistory
from app.models.product import Product


def price_history_window(db: Session, product_id: int) -> list[dict]:
    rows = db.execute(
        select(PriceHistory.price, PriceHistory.captured_at)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.captured_at)
    ).all()
    return [{"price": float(row.price), "captured_at": row.captured_at} for row in rows]


def volatility_score(prices: list[float]) -> float:
    if len(prices) < 2:
        return 0.0
    mean = sum(prices) / len(prices)
    if mean == 0:
        return 0.0
    variance = sum((price - mean) ** 2 for price in prices) / (len(prices) - 1)
    return round((variance ** 0.5) / mean, 4)


def calculate_product_trend(db: Session, product_id: int, window: str = "30d") -> TrendAnalysis:
    history = price_history_window(db, product_id)
    prices = [item["price"] for item in history]
    if len(prices) < 2:
        direction = "stable"
        drop_probability = Decimal("0.2500")
    else:
        change = (prices[-1] - prices[0]) / prices[0]
        direction = "down" if change < -0.02 else "up" if change > 0.02 else "stable"
        drop_probability = Decimal(str(min(max(-change + volatility_score(prices), 0), 1))).quantize(Decimal("0.0001"))
    trend = TrendAnalysis(
        product_id=product_id,
        window=window,
        trend_direction=direction,
        volatility_score=Decimal(str(volatility_score(prices))).quantize(Decimal("0.0001")),
        drop_probability=drop_probability,
        seasonality_score=Decimal("0.2500"),
    )
    db.add(trend)
    db.commit()
    db.refresh(trend)
    return trend


def analytics_heatmap(db: Session) -> list[dict]:
    rows = db.execute(
        text("SELECT category, date, avg_price, count FROM v_category_volatility_heatmap ORDER BY date")
    ).all()
    return [{"category": row[0], "date": str(row[1]), "avg_price": float(row[2] or 0), "count": int(row[3] or 0)} for row in rows]


def retailer_comparison(db: Session, product_id: int) -> list[dict]:
    rows = db.execute(
        text("CALL get_retailer_comparison(:product_id)"),
        {"product_id": product_id}
    ).all()
    return [{"website_id": row[0], "lowest_price": float(row[1] or 0), "average_price": float(row[2] or 0)} for row in rows]
