from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    target_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    channel_email: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    channel_telegram: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    priority: Mapped[str] = mapped_column(String(24), default="normal")
    percentage_drop: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    price_lowest_in_x_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="alerts")
    product = relationship("Product", back_populates="alerts")
