from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import smtplib
from email.message import EmailMessage

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.alert import Alert
from app.models.notification import Notification
from app.models.product import Product
from app.models.user import User


from datetime import datetime, timezone, timedelta
from app.models.price import PriceHistory

def create_price_drop_notifications(db: Session, product: Product, old_price: Decimal, new_price: Decimal) -> None:
    alerts = db.scalars(select(Alert).where(Alert.product_id == product.id, Alert.is_active.is_(True))).all()
    
    for alert in alerts:
        reasons = []
        
        if alert.target_price and alert.target_price >= new_price:
            reasons.append(f"Price reached desired value ({alert.target_price})")
            
        if alert.percentage_drop and old_price > 0:
            drop = ((old_price - new_price) / old_price) * 100
            if drop >= alert.percentage_drop:
                reasons.append(f"Price dropped {alert.percentage_drop}%")
                
        if alert.price_lowest_in_x_days:
            # Check if price is lowest in X days
            date_threshold = datetime.now(timezone.utc) - timedelta(days=alert.price_lowest_in_x_days)
            lowest_in_db = db.scalar(
                select(func.min(PriceHistory.price))
                .where(PriceHistory.product_id == product.id, PriceHistory.captured_at >= date_threshold)
            )
            if lowest_in_db is None or new_price <= lowest_in_db:
                reasons.append(f"Price is lowest in {alert.price_lowest_in_x_days} days")
                
        if reasons:
            savings = old_price - new_price
            reason_str = ", ".join(reasons)
            message = f"{product.title} dropped from {product.currency} {old_price} to {product.currency} {new_price}. Reasons: {reason_str}. Estimated saving: {product.currency} {savings}."
            db.add(Notification(user_id=alert.user_id, product_id=product.id, type="price_drop", title="Smart Alert Triggered", message=message, channel="in_app"))


def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.smtp_host:
        return False
    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(msg)
    return True


async def send_telegram(chat_id: str, text: str) -> bool:
    if not settings.telegram_bot_token:
        return False
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url, json={"chat_id": chat_id, "text": text})
    return response.is_success
