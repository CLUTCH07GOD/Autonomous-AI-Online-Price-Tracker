from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PriceStats(BaseModel):
    current: Decimal | None
    lowest: Decimal | None
    highest: Decimal | None
    average: Decimal | None
    samples: int
