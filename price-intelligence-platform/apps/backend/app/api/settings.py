from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.intelligence import UserPreference
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["settings"])


class PreferencePayload(BaseModel):
    min_discount_pct: Decimal = Decimal("10.00")
    max_budget: Decimal | None = None
    alert_sensitivity: str = "balanced"
    telegram_chat_id: str | None = None


@router.get("/preferences")
def get_preferences(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    pref = db.scalar(select(UserPreference).where(UserPreference.user_id == user.id).limit(1))
    return {
        "name": user.name,
        "email": user.email,
        "telegram_chat_id": user.telegram_chat_id,
        "min_discount_pct": pref.min_discount_pct if pref else Decimal("10.00"),
        "max_budget": pref.max_budget if pref else None,
        "alert_sensitivity": pref.alert_sensitivity if pref else "balanced",
        "scraping_interval": "hourly",
        "theme": "light",
    }


@router.put("/preferences")
def update_preferences(payload: PreferencePayload, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    pref = db.scalar(select(UserPreference).where(UserPreference.user_id == user.id).limit(1))
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
    pref.min_discount_pct = payload.min_discount_pct
    pref.max_budget = payload.max_budget
    pref.alert_sensitivity = payload.alert_sensitivity
    user.telegram_chat_id = payload.telegram_chat_id
    db.commit()
    return get_preferences(db, user)
