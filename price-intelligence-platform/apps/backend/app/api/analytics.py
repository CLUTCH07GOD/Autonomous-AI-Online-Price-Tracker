from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.alert import Alert
from app.models.price import PriceHistory
from app.models.product import Product
from app.schemas.contracts import CategoryAnalytics, DashboardMetrics, HeatmapData, HistoricalAnalytics
from app.models.user import User
from app.services.analytics_engine import analytics_heatmap, volatility_score

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> DashboardMetrics:
    row = db.execute(text("CALL get_dashboard_metrics()")).first()
    return DashboardMetrics(
        total_products=row[0] if row else 0,
        active_alerts=row[1] if row else 0,
        price_drops_24h=row[2] if row else 0,
        total_savings=round(float(row[3] or 0), 2) if row else 0.0,
        average_accuracy=0.92,
    )


@router.get("/category", response_model=list[CategoryAnalytics])
def category_analytics(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    rows = db.execute(
        text("SELECT category, products, average_price FROM v_category_analytics ORDER BY products DESC")
    ).all()
    return [{"category": row[0], "products": row[1], "average_price": round(float(row[2] or 0), 2)} for row in rows]


@router.get("/history", response_model=HistoricalAnalytics)
def history(product_id: int | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    products = db.scalars(select(Product).order_by(Product.created_at.desc()).limit(50)).all()
    selected = product_id or (products[0].id if products else None)
    if not selected:
        return {"products": [], "selected_product_id": None, "history": [], "stats": {"lowest": 0, "highest": 0, "average": 0, "samples": 0}, "volatility": 0}
    rows = db.execute(
        select(PriceHistory.price, PriceHistory.captured_at)
        .where(PriceHistory.product_id == selected)
        .order_by(PriceHistory.captured_at)
    ).all()
    values = [float(row.price) for row in rows]
    stats = {
        "lowest": min(values) if values else 0,
        "highest": max(values) if values else 0,
        "average": round(sum(values) / len(values), 2) if values else 0,
        "samples": len(values),
    }
    return {
        "products": [{"id": item.id, "title": item.title} for item in products],
        "selected_product_id": selected,
        "history": [{"price": float(row.price), "captured_at": row.captured_at.isoformat()} for row in rows],
        "stats": stats,
        "volatility": volatility_score(values),
    }


@router.get("/heatmap", response_model=list[HeatmapData])
def heatmap(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    return analytics_heatmap(db)
