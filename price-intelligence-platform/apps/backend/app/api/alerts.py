from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.alert import Alert
from app.models.notification import Notification
from app.models.user import User
from app.schemas.alert import AlertCreate
from app.schemas.contracts import AlertOutStrict, NotificationOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOutStrict])
def list_alerts(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Alert]:
    return db.scalars(select(Alert).where(Alert.user_id == user.id).order_by(Alert.created_at.desc())).all()


@router.post("", response_model=AlertOutStrict)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Alert:
    alert = Alert(user_id=user.id, **payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}/toggle", response_model=AlertOutStrict)
def toggle_alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Alert:
    alert = db.scalar(select(Alert).where(Alert.id == alert_id, Alert.user_id == user.id))
    if not alert:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_active = not alert.is_active
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/notifications", response_model=list[NotificationOut])
def notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    rows = db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100)).all()
    return [
        {
            "id": item.id,
            "product_id": item.product_id,
            "type": item.type,
            "title": item.title,
            "content": item.message,  # Frontend expects 'content' not 'message'
            "channel": item.channel,
            "created_at": item.created_at,
            "read_at": item.read_at,
        }
        for item in rows
    ]
