from __future__ import annotations

from decimal import Decimal

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ml.anomaly_detection import anomaly_scores, detect_fake_discount
from app.models.intelligence import DiscountAnalysis
from app.models.price import PriceHistory
from app.models.product import Product


def analyze_discount(db: Session, product_id: int) -> DiscountAnalysis:
    product = db.get(Product, product_id)
    if not product or not product.current_best_price:
        raise ValueError("Product not found or missing current price")
    stats = db.execute(
        select(func.avg(PriceHistory.price), func.min(PriceHistory.price), func.max(PriceHistory.price))
        .where(PriceHistory.product_id == product_id)
    ).one()
    history_rows = db.execute(
        select(PriceHistory.price, PriceHistory.captured_at)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.captured_at)
    ).all()
    anomaly_score = 0.0
    if history_rows:
        frame = pd.DataFrame(history_rows, columns=["price", "captured_at"])
        anomaly_score = float(anomaly_scores(frame).iloc[-1])
    result = detect_fake_discount(
        float(product.current_best_price),
        float(product.mrp) if product.mrp else None,
        float(stats[0]) if stats[0] else None,
        float(stats[1]) if stats[1] else None,
        float(stats[2]) if stats[2] else None,
        anomaly_score=anomaly_score,
    )
    analysis = DiscountAnalysis(
        product_id=product_id,
        advertised_discount_pct=Decimal(str(result.get("advertised_discount_pct", 0))),
        real_discount_pct=Decimal(str(result.get("real_discount_pct", 0))),
        inflated_mrp_score=Decimal(str(result.get("inflated_mrp_score", 0))),
        is_fake_discount=bool(result["is_fake_discount"]),
        confidence=Decimal(str(result["confidence"])).quantize(Decimal("0.0001")),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
