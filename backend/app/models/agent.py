"""
Agent identity and wallet model.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    org: Mapped[str] = mapped_column(String(128), nullable=False, default="Unknown")
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    wallet_address: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    reputation_score: Mapped[float] = mapped_column(Float, nullable=False, default=80.0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="online")  # online|idle|offline|frozen
    spend_today: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_frozen: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    policies: Mapped[list["Policy"]] = relationship("Policy", back_populates="agent", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="agent", foreign_keys="Transaction.agent_id")
    kill_switch_events: Mapped[list["KillSwitchEvent"]] = relationship("KillSwitchEvent", back_populates="agent")
