from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductLink(Base):
    __tablename__ = "product_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(Text)
    sku: Mapped[str | None] = mapped_column(String(160), nullable=True)
    last_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    availability: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_checked_at = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    scrape_status: Mapped[str] = mapped_column(String(20), server_default="PENDING")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    product = relationship("Product", back_populates="links")
    website = relationship("Website", back_populates="links")
    history = relationship("PriceHistory", back_populates="product_link")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    product_link_id: Mapped[int] = mapped_column(ForeignKey("product_links.id", ondelete="CASCADE"))
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    mrp: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    availability: Mapped[str | None] = mapped_column(String(80), nullable=True)
    captured_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    product = relationship("Product", back_populates="history")
    product_link = relationship("ProductLink", back_populates="history")
