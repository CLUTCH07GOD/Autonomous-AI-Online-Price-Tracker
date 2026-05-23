from __future__ import annotations

import pandas as pd
from sqlalchemy import select, text

from app.db.session import SessionLocal
from app.jobs.celery_app import celery_app
from app.ml.prediction import forecast_standard_horizons
from app.ml.training import train_all_models
from app.models.price import PriceHistory
from app.models.product import Product
from app.services.analytics_engine import calculate_product_trend
from app.services.discount_service import analyze_discount


import asyncio
from app.services.product_service import refresh_product_prices

@celery_app.task(name="app.jobs.tasks.refresh_prices")
def refresh_prices() -> dict:
    db = SessionLocal()
    try:
        products = db.scalars(select(Product)).all()
        refreshed_count = 0
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            for product in products:
                try:
                    loop.run_until_complete(refresh_product_prices(db, product.id))
                    refreshed_count += 1
                except Exception as e:
                    print(f"Failed to refresh product {product.id}: {e}")
        finally:
            loop.close()
        db.execute(text("CALL refresh_price_daily_analytics()"))
        return {"status": "success", "refreshed_count": refreshed_count}
    finally:
        db.close()


@celery_app.task(name="app.jobs.tasks.train_models")
def train_models() -> dict:
    db = SessionLocal()
    try:
        rows = db.execute(select(PriceHistory.price, PriceHistory.mrp, PriceHistory.captured_at).order_by(PriceHistory.captured_at)).all()
        if len(rows) < 3:
            return {"status": "skipped", "reason": "not enough price history"}
        result = train_all_models(pd.DataFrame(rows, columns=["price", "mrp", "captured_at"]))
        predictions = 0
        discounts = 0
        for product in db.scalars(select(Product)).all():
            calculate_product_trend(db, product.id)
            try:
                predictions += len(forecast_standard_horizons(db, product.id))
            except Exception:
                pass
            try:
                analyze_discount(db, product.id)
                discounts += 1
            except Exception:
                pass
        return {"status": "trained", "predictions": predictions, "discount_scans": discounts, **result}
    finally:
        db.close()
