# Architecture

## Backend

FastAPI hosts a modular REST API:

- `api/`: route modules for auth, products, comparisons, alerts, analytics, predictions.
- `models/`: SQLAlchemy ORM mapped to MySQL.
- `scrapers/`: website adapter registry with Playwright fetching and BeautifulSoup parsing.
- `services/`: product tracking, alert/notification orchestration.
- `ml/`: preprocessing, model training, prediction, discount fraud heuristics.

## Database

The schema is normalized into `users`, `websites`, `products`, `product_links`, `price_history`, `alerts`, `ml_predictions`, and `notifications`.

The enterprise migration adds `categories`, `brands`, `user_preferences`, `recommendation_logs`, `scraper_logs`, `search_history`, `discount_analysis`, `product_reviews`, `trend_analysis`, `competitor_prices`, `purchases`, `audit_logs`, and `price_daily_analytics`.

MySQL does not provide native materialized views, so the project uses:

- `v_product_price_intelligence` as a live analytical SQL view.
- `price_daily_analytics` as a materialized analytics table refreshed through `refresh_price_daily_analytics()`.
- `trg_price_history_alert_audit` to audit every new price sample.

Important indexes:

- product title search.
- product/time price history lookups.
- active alert lookup by user.
- prediction lookup by product and forecast date.

## Frontend

React + TypeScript + Tailwind provides a modern dashboard shell. The UI keeps compact operational patterns from `price-checker-v2`, but now calls REST APIs rather than Electron IPC/local files.

## ML Pipeline

The ML pipeline now includes feature engineering, Random Forest, Linear Regression, optional XGBoost, Prophet-ready dependencies, anomaly detection, drift scoring, recommendation labels, and scheduled retraining.

## Background Processing

Redis + Celery run long-lived jobs:

- scraping queue
- hourly price refresh
- daily retraining
- trend recalculation
- notification orchestration

APScheduler is also available for single-process deployments.
