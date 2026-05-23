from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class PredictionOut(ORMModel):
    id: int
    product_id: int
    model_name: str
    predicted_price: Decimal
    forecast_for: datetime
    confidence: Decimal | None
    signal: str | None
    meta: dict | None = None


class RecommendationOut(BaseModel):
    product_id: int
    title: str
    website: str | None
    current_price: Decimal | None
    reason: str
    score: float
