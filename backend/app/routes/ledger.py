"""
Ledger routes.

GET /ledger   Return tamper-evident ledger entries with transaction data.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ledger import LedgerEntry
from app.models.transaction import Transaction

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("", summary="Retrieve the tamper-evident settlement ledger")
def get_ledger(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Returns ledger entries in reverse-chronological order, enriched with
    transaction data for the frontend Ledger view.
    """
    entries = (
        db.query(LedgerEntry)
        .order_by(LedgerEntry.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = []
    for entry in entries:
        tx: Transaction | None = entry.transaction
        if not tx:
            continue
        result.append({
            "id": entry.id,
            "transaction_id": entry.transaction_id,
            "hash": entry.hash,
            "previous_hash": entry.previous_hash,
            "signer": entry.signer,
            "block_number": entry.block_number,
            "timestamp": entry.timestamp,
            # Denormalized transaction fields
            "display_id": tx.display_id,
            "from": tx.from_agent,
            "to": tx.to_agent,
            "amount": tx.amount,
            "currency": tx.currency,
            "purpose": tx.purpose,
            "status": tx.status,
            "riskScore": tx.risk_score,
            "risk_score": tx.risk_score,
            "latencyMs": tx.latency_ms,
            "latency_ms": tx.latency_ms,
            "policyTrace": json.loads(tx.policy_trace) if tx.policy_trace else [],
        })

    return result
