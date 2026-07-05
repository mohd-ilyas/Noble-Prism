"""
Transaction model — every authorization attempt recorded here.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Human-readable hex-style display id (e.g. 0x4f9a2921)
    display_id: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)

    # Parties
    from_agent: Mapped[str] = mapped_column(String(128), nullable=False)
    to_agent: Mapped[str] = mapped_column(String(128), nullable=False)
    merchant: Mapped[str] = mapped_column(String(256), nullable=False, default="")

    # Value
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")

    # Intent / purpose
    purpose: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="gpu_compute")

    # Scoring
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    intent_score: Mapped[int] = mapped_column(Integer, nullable=False, default=50)

    # Decision
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    # approved | blocked | escalated | pending | rejected

    # Performance
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Policy trace stored as JSON string
    policy_trace: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
        comment="JSON array of {step, detail, passed} objects",
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="transactions", foreign_keys=[agent_id])
    ledger_entry: Mapped["LedgerEntry | None"] = relationship("LedgerEntry", back_populates="transaction", uselist=False)
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="transaction", cascade="all, delete-orphan")
