"""
Kill-switch event — records automatic and manual agent freezes.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class KillSwitchEvent(Base):
    __tablename__ = "kill_switch_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    triggered_by: Mapped[str] = mapped_column(String(32), nullable=False, default="system")  # system | human
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship
    agent: Mapped["Agent"] = relationship("Agent", back_populates="kill_switch_events")
