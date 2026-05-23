from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, HttpUrl

from app.schemas.common import ORMModel, PriceStats


class ProductCreate(BaseModel):
    url: HttpUrl
    target_price: Decimal | None = None


class LinkOut(ORMModel):
    id: int
    url: str
    last_price: Decimal | None
    availability: str | None
    last_checked_at: datetime | None
    scrape_status: str | None = None
    error_message: str | None = None


class ProductOut(ORMModel):
    id: int
    title: str
    brand: str | None
    category: str | None
    image_url: str | None
    currency: str
    current_best_price: Decimal | None
    mrp: Decimal | None
    rating: Decimal | None
    rating_count: int
    links: list[LinkOut] = []


class ProductAnalytics(BaseModel):
    product: ProductOut
    stats: PriceStats
    trend: str
    savings_estimate: Decimal | None
    history: list[dict]
