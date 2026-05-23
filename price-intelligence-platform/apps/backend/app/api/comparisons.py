from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from urllib.parse import urlparse

from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.product import Product
from app.models.user import User
from app.models.price import ProductLink
from app.schemas.contracts import ComparisonResult

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.get("", response_model=list[ComparisonResult])
def compare(q: str | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    stmt = (
        select(Product)
        .options(selectinload(Product.links).selectinload(ProductLink.website))
        .order_by(Product.current_best_price.asc())
    )
    if q:
        stmt = stmt.where(Product.title.ilike(f"%{q}%"))
    products = db.scalars(stmt.limit(30)).all()
    results = []
    for product in products:
        retailers = []
        for link in sorted(product.links, key=lambda item: float(item.last_price or product.current_best_price or 0)):
            parsed = urlparse(link.url)
            domain = parsed.netloc.replace("www.", "") or (link.website.base_url if link.website else "")
            availability = link.availability or "Unknown"
            retailers.append(
                {
                    "name": link.website.name.title() if link.website else domain or "Retailer",
                    "domain": domain,
                    "url": link.url,
                    "price": float(link.last_price or product.current_best_price or 0),
                    "availability": availability,
                    "in_stock": availability.lower() not in {"out of stock", "unavailable", "sold out"},
                    "last_checked_at": link.last_checked_at,
                }
            )
        results.append(
            {
            "id": product.id,
            "title": product.title,
            "image_url": product.image_url,
            "best_price": float(product.current_best_price) if product.current_best_price is not None else None,
            "mrp": float(product.mrp) if product.mrp is not None else None,
            "currency": product.currency,
            "retailers": retailers,
            }
        )
    return results
