from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.price import PriceHistory
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductAnalytics, ProductCreate, ProductOut
from app.services.product_service import add_product_from_url, delete_product, product_stats, refresh_product_prices

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[Product]:
    return db.scalars(select(Product).options(selectinload(Product.links)).order_by(Product.created_at.desc())).all()


@router.post("", response_model=ProductOut)
async def create_product(payload: ProductCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Product:
    try:
        return await add_product_from_url(db, str(payload.url), owner_id=user.id, target_price=payload.target_price)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{product_id}/refresh", response_model=ProductOut)
async def refresh_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Product:
    try:
        return await refresh_product_prices(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{product_id}")
def remove_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    deleted = delete_product(db, product_id, owner_id=user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found or not owned by you")
    return {"status": "deleted", "product_id": product_id}


@router.get("/{product_id}/analytics", response_model=ProductAnalytics)
def analytics(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    product = db.scalar(select(Product).where(Product.id == product_id).options(selectinload(Product.links)))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    history_rows = db.scalars(select(PriceHistory).where(PriceHistory.product_id == product_id).order_by(PriceHistory.captured_at)).all()
    stats = product_stats(db, product_id)
    trend = "stable"
    if len(history_rows) >= 2:
        trend = "down" if history_rows[-1].price < history_rows[0].price else "up" if history_rows[-1].price > history_rows[0].price else "stable"
    savings = (stats["highest"] - product.current_best_price) if stats["highest"] and product.current_best_price else None
    return {
        "product": product,
        "stats": stats,
        "trend": trend,
        "savings_estimate": savings,
        "history": [{"price": row.price, "captured_at": row.captured_at, "website_id": row.website_id} for row in history_rows],
    }
