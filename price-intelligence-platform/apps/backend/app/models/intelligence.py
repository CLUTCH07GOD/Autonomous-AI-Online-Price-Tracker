from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    normalized_name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id", ondelete="SET NULL"), nullable=True)
    min_discount_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), server_default="10.00")
    max_budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    alert_sensitivity: Mapped[str] = mapped_column(String(24), server_default="balanced")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    recommendation_type: Mapped[str] = mapped_column(String(80))
    score: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    reason: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shown_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    clicked_at = mapped_column(DateTime(timezone=True), nullable=True)


class ScraperLog(Base):
    __tablename__ = "scraper_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_link_id: Mapped[int | None] = mapped_column(ForeignKey("product_links.id", ondelete="SET NULL"), nullable=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, server_default="0")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    scraped_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class ScrapeSnapshot(Base):
    __tablename__ = "scrape_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    product_link_id: Mapped[int | None] = mapped_column(ForeignKey("product_links.id", ondelete="SET NULL"), nullable=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    scraped_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    query: Mapped[str] = mapped_column(String(500), index=True)
    filters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result_count: Mapped[int] = mapped_column(Integer, server_default="0")
    searched_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class DiscountAnalysis(Base):
    __tablename__ = "discount_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    advertised_discount_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    real_discount_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    inflated_mrp_score: Mapped[Decimal] = mapped_column(Numeric(6, 4), server_default="0.0000")
    is_fake_discount: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), index=True)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), server_default="0.5000")
    analyzed_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), nullable=True)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, server_default="0")
    sentiment_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    captured_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class TrendAnalysis(Base):
    __tablename__ = "trend_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    window: Mapped[str] = mapped_column(String(24), index=True)
    trend_direction: Mapped[str] = mapped_column(String(24), index=True)
    volatility_score: Mapped[Decimal] = mapped_column(Numeric(8, 4), server_default="0.0000")
    drop_probability: Mapped[Decimal] = mapped_column(Numeric(5, 4), server_default="0.0000")
    seasonality_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), server_default="0.0000")
    calculated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class CompetitorPrice(Base):
    __tablename__ = "competitor_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")
    availability: Mapped[str | None] = mapped_column(String(80), nullable=True)
    captured_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), nullable=True)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    predicted_savings: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    purchased_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    before_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
