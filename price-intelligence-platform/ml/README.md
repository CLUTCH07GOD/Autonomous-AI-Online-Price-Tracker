# ML Module

The runnable ML code lives inside `apps/backend/app/ml` so FastAPI can import it directly:

- `preprocess/`: feature engineering for price history and competitor data.
- `training/`: Linear Regression, Random Forest, XGBoost training with joblib export.
- `prediction/`: future price prediction and buy/wait signal generation.
- `anomaly_detection/`: fake discount and inflated MRP detection.
- `recommendation/`: smart BUY NOW / WAIT / BEST DEAL TODAY scoring.
- `evaluation/`: model drift and quality checks.

This top-level folder is kept for hackathon/presentation clarity and can hold notebooks, exported model artifacts, evaluation reports, and datasets.
