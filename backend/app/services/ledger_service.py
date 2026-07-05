"""
Ledger Service — builds tamper-evident hash-chained entries.
Each entry's hash covers the previous hash + transaction data,
creating an append-only audit chain.
"""
from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.ledger import LedgerEntry
from app.models.transaction import Transaction


_BLOCK_BASE = 18_200_000


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def get_chain_tip(db: Session) -> str:
    """Return the hash of the most recent ledger entry, or genesis hash."""
    last = (
        db.query(LedgerEntry)
        .order_by(LedgerEntry.timestamp.desc())
        .first()
    )
    return last.hash if last else "0" * 64


def append_entry(db: Session, transaction: Transaction) -> LedgerEntry:
    """
    Create and persist a new ledger entry for a settled transaction.
    Computes hash over (previous_hash + tx_id + amount + from + to + timestamp).
    """
    previous_hash = get_chain_tip(db)
    now = datetime.now(timezone.utc)

    payload = json.dumps({
        "prev": previous_hash,
        "tx_id": transaction.id,
        "display_id": transaction.display_id,
        "amount": transaction.amount,
        "from": transaction.from_agent,
        "to": transaction.to_agent,
        "ts": now.isoformat(),
    }, sort_keys=True)

    entry_hash = _sha256(payload)

    # Simulated incrementing block number
    entry_count = db.query(LedgerEntry).count()
    block_number = str(_BLOCK_BASE + entry_count)

    entry = LedgerEntry(
        transaction_id=transaction.id,
        hash=entry_hash,
        previous_hash=previous_hash,
        block_number=block_number,
        timestamp=now,
        signer="aether-core-eu-west-1",
    )
    db.add(entry)
    return entry
