from __future__ import annotations

from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    model_name: Mapped[str] = mapped_column(String(120))
    predicted_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    forecast_for = mapped_column(DateTime(timezone=True), index=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    signal: Mapped[str | None] = mapped_column(String(80), nullable=True)
    meta: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="predictions")
