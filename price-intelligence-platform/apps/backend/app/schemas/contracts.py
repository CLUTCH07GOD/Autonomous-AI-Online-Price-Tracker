from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class DashboardMetrics(BaseModel):
    total_products: int
    active_alerts: int
    price_drops_24h: int
    total_savings: float
    average_accuracy: float


class CategoryAnalytics(BaseModel):
    category: str
    products: int
    average_price: float


class ProductHistoryOption(BaseModel):
    id: int
    title: str


class ProductHistoryPoint(BaseModel):
    price: float
    captured_at: str


class HistoricalStats(BaseModel):
    lowest: float = 0
    highest: float = 0
    average: float = 0
    samples: int = 0


class HistoricalAnalytics(BaseModel):
    products: list[ProductHistoryOption]
    selected_product_id: int | None
    history: list[ProductHistoryPoint]
    stats: HistoricalStats
    volatility: float


class HeatmapData(BaseModel):
    category: str
    date: str
    avg_price: float
    count: int


class Recommendation(BaseModel):
    id: int
    product_id: int
    title: str
    type: str
    content: str
    score: float
    created_at: datetime | None = None


class NotificationOut(BaseModel):
    id: int
    product_id: int | None = None
    type: str
    title: str
    content: str
    channel: str
    created_at: datetime
    read_at: datetime | None = None


class ComparisonRetailer(BaseModel):
    name: str
    domain: str
    url: str
    price: float
    availability: str | None = None
    in_stock: bool
    last_checked_at: datetime | None = None


class ComparisonResult(BaseModel):
    id: int
    title: str
    image_url: str | None = None
    best_price: float | None = None
    mrp: float | None = None
    currency: str
    retailers: list[ComparisonRetailer]


class HealthComponents(BaseModel):
    backend: str
    database: str
    database_schema: str = "unknown"
    database_procedures: str = "unknown"
    database_views: str = "unknown"
    scraper: str
    ml_engine: str


class HealthStatus(BaseModel):
    status: str
    components: HealthComponents
    version: str
    checked_at: datetime


class AlertOutStrict(ORMModel):
    id: int
    product_id: int
    target_price: Decimal
    channel_email: bool
    channel_telegram: bool
    is_active: bool
    priority: str
    percentage_drop: Decimal | None = None
    price_lowest_in_x_days: int | None = None
    created_at: datetime | None = None
