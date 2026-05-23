from __future__ import annotations

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "price_intelligence",
    broker=settings.redis_url,
    backend=settings.redis_url.replace("/0", "/1"),
)

celery_app.conf.beat_schedule = {
    "hourly-price-refresh": {"task": "app.jobs.tasks.refresh_prices", "schedule": 3600.0},
    "daily-model-training": {"task": "app.jobs.tasks.train_models", "schedule": 86400.0},
}
