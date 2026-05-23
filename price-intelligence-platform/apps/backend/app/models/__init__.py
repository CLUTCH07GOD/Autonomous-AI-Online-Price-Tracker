from __future__ import annotations

from app.models.alert import Alert
from app.models.notification import Notification
from app.models.prediction import MLPrediction
from app.models.price import PriceHistory, ProductLink
from app.models.product import Product
from app.models.user import User
from app.models.website import Website
from app.models.intelligence import (
    AuditLog,
    Brand,
    Category,
    CompetitorPrice,
    DiscountAnalysis,
    ProductReview,
    Purchase,
    RecommendationLog,
    ScrapeSnapshot,
    ScraperLog,
    SearchHistory,
    TrendAnalysis,
    UserPreference,
)

__all__ = [
    "Alert",
    "Notification",
    "MLPrediction",
    "PriceHistory",
    "ProductLink",
    "Product",
    "User",
    "Website",
    "AuditLog",
    "Brand",
    "Category",
    "CompetitorPrice",
    "DiscountAnalysis",
    "ProductReview",
    "Purchase",
    "RecommendationLog",
    "ScrapeSnapshot",
    "ScraperLog",
    "SearchHistory",
    "TrendAnalysis",
    "UserPreference",
]
