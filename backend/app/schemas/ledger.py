"""
Pydantic v2 schemas for the Ledger endpoint.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LedgerEntryResponse(BaseModel):
    id: str
    transaction_id: str
    hash: str
    previous_hash: str
    signer: str
    block_number: str
    timestamp: datetime

    # Denormalized transaction fields for frontend convenience
    display_id: str
    from_agent: str
    to_agent: str
    amount: float
    currency: str
    status: str
    risk_score: float
    latency_ms: int

    model_config = {"from_attributes": True}
