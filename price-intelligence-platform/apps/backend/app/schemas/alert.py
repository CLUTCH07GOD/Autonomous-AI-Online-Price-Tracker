from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class AlertCreate(BaseModel):
    product_id: int
    target_price: Decimal
    channel_email: bool = True
    channel_telegram: bool = False
    percentage_drop: Decimal | None = None
    price_lowest_in_x_days: int | None = None


class AlertOut(ORMModel):
    id: int
    product_id: int
    target_price: Decimal
    channel_email: bool
    channel_telegram: bool
    is_active: bool
    priority: str
    percentage_drop: Decimal | None = None
    price_lowest_in_x_days: int | None = None
