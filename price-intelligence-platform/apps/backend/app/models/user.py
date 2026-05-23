from __future__ import annotations

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="user")
    telegram_chat_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="owner")
    alerts = relationship("Alert", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
