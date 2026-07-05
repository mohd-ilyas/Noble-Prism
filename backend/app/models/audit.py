"""
Audit log — immutable event record for every meaningful system action.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str | None] = mapped_column(
        ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # e.g. TRANSACTION_APPROVED, TRANSACTION_BLOCKED, KILL_SWITCH_ACTIVATED, POLICY_UPDATED ...
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    dot: Mapped[str] = mapped_column(String(16), nullable=False, default="primary")
    # success | warning | danger | primary | secondary
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)

    # Relationship
    transaction: Mapped["Transaction | None"] = relationship("Transaction", back_populates="audit_logs")
