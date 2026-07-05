"""
Pydantic v2 schemas for Transactions.
All response shapes mirror the frontend Transaction interface.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Request bodies ──────────────────────────────────────────────────────────

class TransactionEvaluateRequest(BaseModel):
    """Dry-run evaluation — no side effects."""
    from_agent: str = Field(..., alias="from")
    to_agent: str = Field(..., alias="to")
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    category: str = Field(default="gpu_compute")
    purpose: str = Field(default="")
    merchant: str = Field(default="")

    model_config = {"populate_by_name": True}


class TransactionInitiateRequest(BaseModel):
    """Initiate a real transaction through the full policy/risk pipeline."""
    from_agent: str = Field(..., alias="from")
    to_agent: str = Field(..., alias="to")
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    category: str = Field(default="gpu_compute")
    purpose: str = Field(default="")
    merchant: str = Field(default="")

    model_config = {"populate_by_name": True}


class TransactionApproveRequest(BaseModel):
    transaction_id: str
    operator_note: str = Field(default="")


class TransactionRejectRequest(BaseModel):
    transaction_id: str
    reason: str = Field(default="")


# ── Embedded sub-models ─────────────────────────────────────────────────────

class PolicyTraceStep(BaseModel):
    step: str
    detail: str
    passed: bool


# ── Response shapes (frontend-compatible) ───────────────────────────────────

class TransactionResponse(BaseModel):
    """
    Matches the frontend Transaction interface exactly:
      id, from, to, amount, currency, purpose, status,
      riskScore, timestamp, latencyMs, policyTrace
    """
    id: str
    from_: str = Field(alias="from")
    to: str
    amount: float
    currency: str
    purpose: str
    status: str
    riskScore: float
    timestamp: str           # HH:MM:SS display string
    latencyMs: int
    policyTrace: list[PolicyTraceStep]
    # Extended fields (backend-only consumers)
    category: str = ""
    merchant: str = ""
    intent_score: int = 50
    created_at: Optional[datetime] = None

    model_config = {"populate_by_name": True, "from_attributes": True}


class EvaluationResult(BaseModel):
    """Result from /transactions/evaluate (dry-run)."""
    decision: str                  # approved | blocked | human_approval_required
    intent_score: int
    risk_score: float
    reason: str
    policy_trace: list[PolicyTraceStep]
    latency_ms: int


class KillSwitchResponse(BaseModel):
    agent_id: str
    reason: str
    risk_score: float
    triggered_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    status: str  # active | released
