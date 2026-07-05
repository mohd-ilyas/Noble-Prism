"""
Transaction routes — the core authorization engine.

POST /transactions/evaluate   Dry-run evaluation (no side effects)
POST /transactions/initiate   Full pipeline execution
POST /transactions/approve    Human approval of escalated transaction
POST /transactions/reject     Human rejection of escalated transaction
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionApproveRequest,
    TransactionEvaluateRequest,
    TransactionInitiateRequest,
    TransactionRejectRequest,
)
from app.services import audit_service, ledger_service
from app.services.transaction_service import process_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/evaluate", summary="Dry-run policy evaluation (no persistence)")
def evaluate_transaction(body: TransactionEvaluateRequest, db: Session = Depends(get_db)):
    """
    Evaluate a transaction request against all policy rules without committing
    anything to the database.  Returns decision, scores, and policy trace.
    """
    result = process_transaction(
        db,
        from_agent=body.from_agent,
        to_agent=body.to_agent,
        amount=body.amount,
        currency=body.currency,
        category=body.category,
        purpose=body.purpose,
        merchant=body.merchant,
        dry_run=True,
    )
    return {
        "decision": result["decision"],
        "intent_score": result["intent_score"],
        "risk_score": result["risk_score"],
        "reason": result["reason"],
        "latency_ms": result["latency_ms"],
        "policy_trace": result["policyTrace"],
    }


@router.post("/initiate", status_code=status.HTTP_201_CREATED, summary="Initiate a real transaction")
def initiate_transaction(body: TransactionInitiateRequest, db: Session = Depends(get_db)):
    """
    Run the complete authorization pipeline and persist all results.
    This is the primary payment endpoint.
    """
    result = process_transaction(
        db,
        from_agent=body.from_agent,
        to_agent=body.to_agent,
        amount=body.amount,
        currency=body.currency,
        category=body.category,
        purpose=body.purpose,
        merchant=body.merchant,
        dry_run=False,
    )
    return result


@router.post("/approve", summary="Human approval of an escalated transaction")
def approve_transaction(body: TransactionApproveRequest, db: Session = Depends(get_db)):
    """
    Operator approves a transaction that was escalated for human review.
    Commits it to the ledger.
    """
    tx = db.query(Transaction).filter(
        (Transaction.id == body.transaction_id) | (Transaction.display_id == body.transaction_id)
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if tx.status not in ("escalated", "pending"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Transaction in status '{tx.status}' cannot be approved",
        )

    tx.status = "approved"

    # Update agent spend
    from app.models.agent import Agent
    agent = db.query(Agent).filter(Agent.id == tx.agent_id).first()
    if agent:
        agent.spend_today = round(agent.spend_today + tx.amount, 2)

    # Commit to ledger
    ledger_service.append_entry(db, tx)
    audit_service.log(
        db,
        event_type="TRANSACTION_APPROVED",
        description=f"Human-approved ${tx.amount:.2f} {tx.currency} from {tx.from_agent}. Note: {body.operator_note}",
        transaction_id=tx.id,
        agent_id=tx.agent_id,
        metadata={"operator_note": body.operator_note},
    )

    db.commit()
    db.refresh(tx)

    trace = json.loads(tx.policy_trace)
    return {
        "id": tx.display_id,
        "status": tx.status,
        "from": tx.from_agent,
        "to": tx.to_agent,
        "amount": tx.amount,
        "currency": tx.currency,
        "policyTrace": trace,
        "riskScore": tx.risk_score,
        "latencyMs": tx.latency_ms,
        "message": "Transaction approved by operator",
    }


@router.post("/reject", summary="Human rejection of an escalated transaction")
def reject_transaction(body: TransactionRejectRequest, db: Session = Depends(get_db)):
    """
    Operator rejects a transaction that was escalated for human review.
    """
    tx = db.query(Transaction).filter(
        (Transaction.id == body.transaction_id) | (Transaction.display_id == body.transaction_id)
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if tx.status not in ("escalated", "pending"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Transaction in status '{tx.status}' cannot be rejected",
        )

    tx.status = "blocked"
    audit_service.log(
        db,
        event_type="TRANSACTION_REJECTED",
        description=f"Human-rejected ${tx.amount:.2f} {tx.currency} from {tx.from_agent}. Reason: {body.reason}",
        transaction_id=tx.id,
        agent_id=tx.agent_id,
        metadata={"reason": body.reason},
    )

    db.commit()
    db.refresh(tx)

    trace = json.loads(tx.policy_trace)
    return {
        "id": tx.display_id,
        "status": tx.status,
        "from": tx.from_agent,
        "to": tx.to_agent,
        "amount": tx.amount,
        "currency": tx.currency,
        "policyTrace": trace,
        "riskScore": tx.risk_score,
        "latencyMs": tx.latency_ms,
        "message": "Transaction rejected by operator",
    }
