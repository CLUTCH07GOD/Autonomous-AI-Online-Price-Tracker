from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ml.recommendation import popularity_score, price_drop_score, recommendation_label, recommendation_score
from app.models.intelligence import RecommendationLog, TrendAnalysis
from app.models.price import PriceHistory
from app.models.product import Product


def generate_recommendations(db: Session, user_id: int | None = None, limit: int = 20) -> list[dict]:
    products = db.scalars(select(Product).where(Product.current_best_price.is_not(None)).limit(200)).all()
    output: list[dict] = []
    for product in products:
        historical_avg = db.scalar(select(func.avg(PriceHistory.price)).where(PriceHistory.product_id == product.id))
        latest_trend = db.scalar(
            select(TrendAnalysis)
            .where(TrendAnalysis.product_id == product.id)
            .order_by(TrendAnalysis.calculated_at.desc())
            .limit(1)
        )
        current = float(product.current_best_price or 0)
        mrp = float(product.mrp or current or 1)
        avg = float(historical_avg or current or 1)
        discount = max((mrp - current) / mrp, 0) if mrp else 0
        competitor_gap = max((avg - current) / avg, 0) if avg else 0
        drop_probability = float(latest_trend.drop_probability) if latest_trend else 0.35
        volatility = float(latest_trend.volatility_score) if latest_trend else 0.0
        rating_score = float(product.rating or 0) / 5
        popularity = popularity_score(float(product.rating or 0), product.rating_count)
        drop_score = price_drop_score(current, avg, float(product.lowest_price) if product.lowest_price else None)
        confidence = max(0.45, min(0.92, 0.78 - volatility))
        score = recommendation_score(
            discount,
            drop_probability,
            confidence,
            competitor_gap,
            rating_score=rating_score,
            volatility=volatility,
            popularity=popularity,
            price_drop=drop_score,
        )
        label = recommendation_label(score, drop_probability)
        reason = (
            f"{label}: {discount * 100:.1f}% discount, {drop_score * 100:.1f}% price-drop score, "
            f"{popularity * 100:.1f}% popularity, volatility {volatility * 100:.1f}%."
        )
        log = RecommendationLog(
                user_id=user_id,
                product_id=product.id,
                recommendation_type=label,
                score=Decimal(str(score)),
                reason=reason,
                model_name="hybrid_kmeans_inspired_v2",
        )
        db.add(log)
        output.append({"product_id": product.id, "title": product.title, "score": score, "label": label, "reason": reason, "current_price": product.current_best_price, "created_at": log.shown_at})
    db.commit()
    return sorted(output, key=lambda item: item["score"], reverse=True)[:limit]
