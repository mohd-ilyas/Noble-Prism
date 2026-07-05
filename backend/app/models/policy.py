"""
Spending policy model — per-agent rules evaluated at authorization time.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, default="default-policy")
    scope: Mapped[str] = mapped_column(String(128), nullable=False, default="All agents")
    daily_limit: Mapped[float] = mapped_column(Float, nullable=False, default=100_000.0)
    allowed_categories: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="gpu_compute,inference,data,storage,api",
        comment="Comma-separated list of allowed category strings",
    )
    max_transaction_amount: Mapped[float] = mapped_column(Float, nullable=False, default=5_000.0)
    approval_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=1_000.0)
    velocity_limit_per_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=40)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")  # active|monitor|disabled
    triggers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blocks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="policies")
