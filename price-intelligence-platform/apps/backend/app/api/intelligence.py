from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.cache import cache, cache_key
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import select
from app.models.intelligence import DiscountAnalysis, TrendAnalysis
from app.services.analytics_engine import analytics_heatmap, calculate_product_trend, retailer_comparison
from app.services.discount_service import analyze_discount
from app.services.recommendation_service import generate_recommendations
from app.schemas.contracts import HeatmapData, Recommendation

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/heatmap", response_model=list[HeatmapData])
def heatmap(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    key = cache_key("heatmap")
    cached = cache.get(key)
    if cached is not None:
        return cached
    result = analytics_heatmap(db)
    cache.set(key, result, ttl_seconds=300)
    return result


@router.get("/trends")
def trend_list(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    rows = db.scalars(select(TrendAnalysis).order_by(TrendAnalysis.calculated_at.desc()).limit(100)).all()
    return [
        {
            "id": row.id,
            "product_id": row.product_id,
            "window": row.window,
            "trend_direction": row.trend_direction,
            "volatility_score": row.volatility_score,
            "drop_probability": row.drop_probability,
            "seasonality_score": row.seasonality_score,
            "calculated_at": row.calculated_at,
        }
        for row in rows
    ]


@router.post("/trends/{product_id}")
def calculate_trend(product_id: int, window: str = Query("30d"), db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    trend = calculate_product_trend(db, product_id, window=window)
    return {
        "id": trend.id,
        "product_id": trend.product_id,
        "window": trend.window,
        "trend_direction": trend.trend_direction,
        "volatility_score": trend.volatility_score,
        "drop_probability": trend.drop_probability,
        "seasonality_score": trend.seasonality_score,
    }


@router.post("/discounts/{product_id}")
def discount_detector(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> dict:
    try:
        analysis = analyze_discount(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {
        "id": analysis.id,
        "product_id": analysis.product_id,
        "advertised_discount_pct": analysis.advertised_discount_pct,
        "real_discount_pct": analysis.real_discount_pct,
        "inflated_mrp_score": analysis.inflated_mrp_score,
        "is_fake_discount": analysis.is_fake_discount,
        "confidence": analysis.confidence,
    }


@router.get("/discounts")
def discount_list(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    rows = db.scalars(select(DiscountAnalysis).order_by(DiscountAnalysis.analyzed_at.desc()).limit(100)).all()
    return [
        {
            "id": row.id,
            "product_id": row.product_id,
            "advertised_discount_pct": row.advertised_discount_pct,
            "real_discount_pct": row.real_discount_pct,
            "inflated_mrp_score": row.inflated_mrp_score,
            "is_fake_discount": row.is_fake_discount,
            "confidence": row.confidence,
            "analyzed_at": row.analyzed_at,
        }
        for row in rows
    ]


@router.get("/automation/status")
def automation_status(_: User = Depends(get_current_user)) -> dict:
    return {
        "scraping": {"schedule": "hourly", "queue": "celery", "status": "configured"},
        "training": {"schedule": "daily 02:15 UTC", "models": ["linear_regression", "random_forest", "xgboost"], "status": "configured"},
        "alerts": {"priority_ai": True, "channels": ["in_app", "email", "telegram"]},
    }


@router.get("/recommendations", response_model=list[Recommendation])
def recommendation_center(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    raw = generate_recommendations(db, user_id=user.id, limit=limit)
    # Map to frontend Recommendation type: id, product_id, title, type, content, score, created_at
    return [
        {
            "id": idx + 1,
            "product_id": item["product_id"],
            "title": item["title"],
            "type": item.get("label", "WAIT"),
            "content": item.get("reason", ""),
            "score": item["score"],
            "created_at": item.get("created_at"),
        }
        for idx, item in enumerate(raw)
    ]


@router.get("/retailers/{product_id}")
def retailers(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    return retailer_comparison(db, product_id)


from pydantic import BaseModel
from app.scrapers.price_parser import normalize_price, detect_currency

class ParseTestRequest(BaseModel):
    raw_text: str
    locale_hint: str = "AUTO"

REFERENCES_DATA = [
    {
        "id": "ecommerce-price-scraper",
        "title": "E-Commerce Price Scraper & Toolkit",
        "description": "Production-grade price scraping pipeline with international locale normalization, marketing cleanup, multi-variant AI extraction, proxy rotation, and anti-bot evasion.",
        "path": "references/ecommerce-price-scraper-main",
        "features": [
            "Multi-locale price parsing (Decimal-precise)",
            "Marketing noise filter (regex cleaning patterns)",
            "Symbol & geo-context currency resolution",
            "Hierarchical fallback selectors (JSON-LD -> microdata -> CSS)",
            "Playwright browser network interception",
            "LLM-based unstructured price extraction"
        ],
        "tech_stack": ["Playwright", "BeautifulSoup4", "SQLite", "Requests"],
        "integration_points": [
            {
                "feature": "Locale & Currency Normalization",
                "file": "apps/backend/app/scrapers/price_parser.py",
                "status": "Production Merged"
            },
            {
                "feature": "Structured Data Fallbacks",
                "file": "apps/backend/app/scrapers/adapters.py",
                "status": "Production Merged"
            }
        ]
    },
    {
        "id": "stock-prediction-deep-learning",
        "title": "Deep Learning Stock & Price Forecasting",
        "description": "Multivariate LSTM neural networks and Prophet time-series models for forecasting price trends, volatility metrics, and buy/sell signals.",
        "path": "references/stock-prediction-deep-neural-learning-master",
        "features": [
            "Multivariate LSTM neural network modeling",
            "Prophet-based seasonality and trend decomposed charts",
            "Rolling-window buy/sell confidence thresholds",
            "High-frequency training pipeline & model evaluation"
        ],
        "tech_stack": ["TensorFlow/Keras", "Prophet", "scikit-learn", "numpy", "pandas"],
        "integration_points": [
            {
                "feature": "AI Price Forecasting Engine",
                "file": "apps/backend/app/ml/prediction/forecaster.py",
                "status": "Integrated"
            },
            {
                "feature": "AI Insights Timelines",
                "file": "apps/frontend/src/pages/AIInsights.tsx",
                "status": "Active"
            }
        ]
    },
    {
        "id": "product-recommendations",
        "title": "Collaborative Product Recommendation Engine",
        "description": "Hybrid K-Means and Collaborative Filtering recommendation system, computing similarity matrices to suggest alternative platforms and target deals.",
        "path": "references/product-recommendations-main",
        "features": [
            "User-item collaborative filtering",
            "Product attribute clustering (K-Means)",
            "Target price drop recommendation trigger",
            "Highly scalable similarity matrix calculation"
        ],
        "tech_stack": ["scikit-learn", "pandas", "numpy", "joblib"],
        "integration_points": [
            {
                "feature": "Recommendation Generator",
                "file": "apps/backend/app/services/recommendation_service.py",
                "status": "Active"
            },
            {
                "feature": "Recommendation Center Screen",
                "file": "apps/frontend/src/pages/RecommendationPage.tsx",
                "status": "Active"
            }
        ]
    },
    {
        "id": "fraud-anomaly-detection",
        "title": "Autoencoder-based Fraud & Anomaly Detection",
        "description": "Unsupervised Autoencoder neural networks and isolation forests to identify fake discounts, inflated MSRPs, and suspicious pricing drops.",
        "path": "references/Fraud-Detection-main",
        "features": [
            "Unsupervised deep autoencoders for reconstruction loss",
            "Isolation Forest multi-dimensional outlier detection",
            "Authenticity scores for retail discounts",
            "Suspicious price change flagging"
        ],
        "tech_stack": ["Keras", "scikit-learn", "numpy", "pandas"],
        "integration_points": [
            {
                "feature": "Fake Discount Classifier",
                "file": "apps/backend/app/services/discount_service.py",
                "status": "Active"
            },
            {
                "feature": "Fake Discount Detector Screen",
                "file": "apps/frontend/src/pages/DiscountPage.tsx",
                "status": "Active"
            }
        ]
    }
]


@router.get("/references")
def get_references(_: User = Depends(get_current_user)) -> list[dict]:
    return REFERENCES_DATA


@router.post("/references/parse")
def parse_reference_test(payload: ParseTestRequest, _: User = Depends(get_current_user)) -> dict:
    import re
    raw_text = payload.raw_text
    locale = payload.locale_hint
    
    # Run exact reference marketing cleanup heuristic
    cleaned_marketing = raw_text
    if raw_text:
        # Match standard marketing patterns: "Was X Now Y" or "Save Z%"
        # Remove was price part and get final price part
        matches = re.findall(r"(?:now|current|sale)?\s*[\$\u20AC\u00A3\u20B9\u00A5]?\s*\d+[\.,]\d+", raw_text, re.IGNORECASE)
        if len(matches) > 1:
            cleaned_marketing = matches[-1] # take final price
    
    parsed_price = normalize_price(cleaned_marketing, locale)
    currency_code = detect_currency(raw_text)
    
    return {
        "raw_text": raw_text,
        "locale_hint": locale,
        "cleaned_marketing": cleaned_marketing,
        "parsed_price": float(parsed_price) if parsed_price else None,
        "currency": currency_code,
        "status": "success"
    }

