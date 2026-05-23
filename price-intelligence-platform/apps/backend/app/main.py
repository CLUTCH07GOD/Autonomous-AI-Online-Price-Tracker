from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api import alerts, analytics, auth, comparisons, intelligence, predictions, products, settings as settings_api
from app.core.config import settings
from app.jobs.scheduler import start_scheduler
from app.schemas.contracts import HealthStatus

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("price_intelligence.api")

app = FastAPI(title="Price Intelligence API", version="1.0.0")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(comparisons.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(intelligence.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")


@app.on_event("startup")
def startup_jobs() -> None:
    if getattr(app.state, "scheduler", None):
        return
    try:
        app.state.scheduler = start_scheduler()
        logger.info("scheduler_started jobs=%s", [job.id for job in app.state.scheduler.get_jobs()])
    except Exception as exc:
        logger.warning("scheduler_start_failed error=%r", exc)


@app.on_event("shutdown")
def shutdown_jobs() -> None:
    scheduler = getattr(app.state, "scheduler", None)
    if scheduler:
        scheduler.shutdown(wait=False)


@app.middleware("http")
async def structured_request_logging(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    logger.info(
        "request_completed method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
    )
    return response


def build_health_status() -> dict:
    components = {
        "backend": "ok",
        "database": "unknown",
        "database_schema": "unknown",
        "database_procedures": "unknown",
        "database_views": "unknown",
        "scraper": "configured",
        "ml_engine": "configured",
    }
    try:
        from app.db.session import SessionLocal

        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            required_tables = {
                "users",
                "websites",
                "products",
                "product_links",
                "price_history",
                "alerts",
                "ml_predictions",
                "notifications",
                "scraper_logs",
                "competitor_prices",
                "price_daily_analytics",
            }
            required_procedures = {
                "refresh_price_daily_analytics",
                "get_retailer_comparison",
                "get_dashboard_metrics",
                "record_price_snapshot",
                "log_scrape_result",
                "create_alert",
                "get_price_trend",
                "upsert_product",
            }
            required_views = {
                "v_product_price_intelligence",
                "v_category_volatility_heatmap",
                "v_category_analytics",
            }

            db_name = db.execute(text("SELECT DATABASE()")).scalar()
            existing_tables = {
                row[0]
                for row in db.execute(
                    text(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = :schema"
                    ),
                    {"schema": db_name},
                )
            }
            existing_procedures = {
                row[0]
                for row in db.execute(
                    text(
                        "SELECT routine_name FROM information_schema.routines WHERE routine_schema = :schema AND routine_type = 'PROCEDURE'"
                    ),
                    {"schema": db_name},
                )
            }
            existing_views = {
                row[0]
                for row in db.execute(
                    text(
                        "SELECT table_name FROM information_schema.views WHERE table_schema = :schema"
                    ),
                    {"schema": db_name},
                )
            }

            missing_tables = required_tables.difference(existing_tables)
            missing_procedures = required_procedures.difference(existing_procedures)
            missing_views = required_views.difference(existing_views)

            components["database"] = "ok" if not (missing_tables or missing_procedures or missing_views) else "degraded"
            components["database_schema"] = "ok" if not missing_tables else f"missing: {', '.join(sorted(missing_tables))[:120]}"
            components["database_procedures"] = "ok" if not missing_procedures else f"missing: {', '.join(sorted(missing_procedures))[:120]}"
            components["database_views"] = "ok" if not missing_views else f"missing: {', '.join(sorted(missing_views))[:120]}"
        finally:
            db.close()
    except Exception as exc:
        components["database"] = f"error: {str(exc)[:100]}"

    return {
        "status": "ok" if components["database"] == "ok" else "degraded",
        "components": components,
        "version": "1.0.0",
        "checked_at": datetime.now(timezone.utc),
    }


@app.get("/health", response_model=HealthStatus)
def health() -> dict:
    """Detailed platform health check."""
    return build_health_status()


@app.get("/api/health", response_model=HealthStatus)
def api_health() -> dict:
    """Detailed API health check with component statuses."""
    return build_health_status()
