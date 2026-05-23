from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.ml.prediction import forecast_price, forecast_standard_horizons
from app.models.prediction import MLPrediction
from app.models.product import Product
from app.models.user import User
from app.schemas.prediction import PredictionOut, RecommendationOut

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/{product_id}", response_model=PredictionOut)
def create_prediction(product_id: int, days: int = 7, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> MLPrediction:
    try:
        return forecast_price(db, product_id, days=days)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{product_id}/standard", response_model=list[PredictionOut])
def create_standard_predictions(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[MLPrediction]:
    try:
        return forecast_standard_horizons(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("", response_model=list[PredictionOut])
def list_predictions(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[MLPrediction]:
    return db.scalars(select(MLPrediction).order_by(MLPrediction.created_at.desc()).limit(50)).all()


@router.get("/recommendations/deals", response_model=list[RecommendationOut])
def recommendations(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    products = db.scalars(select(Product).order_by(Product.current_best_price.asc()).limit(20)).all()
    recs = []
    for product in products:
        if not product.current_best_price:
            continue
        discount = float(((product.mrp or product.current_best_price) - product.current_best_price) / (product.mrp or product.current_best_price))
        score = discount * 0.65 + min((product.rating_count or 0) / 10000, 1) * 0.2 + float(product.rating or 0) / 5 * 0.15
        recs.append({"product_id": product.id, "title": product.title, "website": product.links[0].website.name if product.links else None, "current_price": product.current_best_price, "reason": "Strong discount with healthy demand signals", "score": round(score, 3)})
    return sorted(recs, key=lambda item: item["score"], reverse=True)[:10]
