# ML System

The backend ML system is organized for production growth:

- `preprocess/`: time, rolling, volatility, discount, and competitor features.
- `training/`: Linear Regression, Random Forest, XGBoost with grid search where useful.
- `prediction/`: next-day, weekly, and monthly price forecasting hooks.
- `recommendation/`: BUY NOW, WAIT, HIGH CHANCE OF DROP, BEST DEAL TODAY logic.
- `anomaly_detection/`: fake discount and inflated MRP detection.
- `evaluation/`: drift scoring and model health checks.
- `models/`: persisted joblib artifacts.
- `datasets/`: offline exports and training snapshots.

Prophet is included in dependencies for time-series extension. The current code keeps a safe fallback path so the app can still run when optional heavy ML packages are not installed during lightweight development.

## Automated Training

Celery beat schedules:

- hourly price refresh queue
- daily model training
- trend recomputation after model training

Run:

```bash
celery -A app.jobs.celery_app.celery_app worker --loglevel=INFO
celery -A app.jobs.celery_app.celery_app beat --loglevel=INFO
```
