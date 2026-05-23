from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.jobs.tasks import refresh_prices, train_models


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(train_models, "cron", hour=2, minute=15, id="daily_model_training", replace_existing=True)
    scheduler.add_job(refresh_prices, "interval", hours=1, id="hourly_price_refresh", replace_existing=True, max_instances=1)
    scheduler.start()
    return scheduler
