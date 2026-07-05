"""
Ledger entry — tamper-evident hash chain anchoring every settled transaction.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="0" * 64)
    signer: Mapped[str] = mapped_column(String(128), nullable=False, default="aether-core-eu-west-1")
    block_number: Mapped[str] = mapped_column(String(20), nullable=False, default="0")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)

    # Relationship
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="ledger_entry")
