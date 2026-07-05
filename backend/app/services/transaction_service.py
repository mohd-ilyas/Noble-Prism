"""
Transaction Service — orchestrates the full authorization pipeline:
  1. Identity lookup
  2. Velocity check / kill-switch trigger (RULE 3)
  3. Policy engine evaluation (RULES 1, 2, 4)
  4. Ledger commit (approved only)
  5. Audit logging
  6. Reputation update
"""
from __future__ import annotations

import json
import random
import string
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.policy import Policy
from app.models.transaction import Transaction
from app.models import KillSwitchEvent
from app.schemas.transaction import PolicyTraceStep
from app.services import audit_service, ledger_service, velocity_service
from app.services.policy_engine import evaluate, PolicyDecision


def _generate_display_id() -> str:
    """Generate a hex-style display ID like 0x4f9a2921."""
    return "0x" + "".join(random.choices("0123456789abcdef", k=8))


def _get_agent(db: Session, name: str) -> Agent | None:
    return db.query(Agent).filter(Agent.name == name).first()


def _get_policy(db: Session, agent_id: str) -> Policy | None:
    return (
        db.query(Policy)
        .filter(Policy.agent_id == agent_id, Policy.status != "disabled")
        .order_by(Policy.created_at.desc())
        .first()
    )


def _agent_avg_tx(db: Session, agent_id: str) -> float:
    from sqlalchemy import func
    avg = (
        db.query(func.avg(Transaction.amount))
        .filter(Transaction.agent_id == agent_id, Transaction.status == "approved")
        .scalar()
    )
    return float(avg) if avg else 0.0


def _freeze_agent(db: Session, agent: Agent, reason: str, risk_score: float) -> None:
    """Freeze an agent and create a kill-switch event record."""
    agent.is_frozen = True
    agent.status = "offline"
    ks = KillSwitchEvent(
        agent_id=agent.id,
        reason=reason,
        risk_score=risk_score,
        triggered_by="system",
    )
    db.add(ks)
    audit_service.log(
        db,
        event_type="KILL_SWITCH_ACTIVATED",
        description=f"Kill switch activated for {agent.name}: {reason}",
        agent_id=agent.id,
        metadata={"risk_score": risk_score, "reason": reason},
    )


def _update_reputation(db: Session, agent: Agent, decision: str) -> None:
    """
    Adjust agent reputation based on transaction outcome.
    Approved transactions improve reputation slightly; blocked/escalated worsen it.
    """
    delta = {"approved": 0.1, "blocked": -0.5, "escalated": -0.2, "human_approval_required": -0.1}.get(decision, 0)
    agent.reputation_score = round(max(0.0, min(100.0, agent.reputation_score + delta)), 2)


def process_transaction(
    db: Session,
    *,
    from_agent: str,
    to_agent: str,
    amount: float,
    currency: str,
    category: str,
    purpose: str,
    merchant: str,
    dry_run: bool = False,
) -> dict:
    """
    Full authorization pipeline.  Returns a dict with all decision fields.
    If dry_run=True, nothing is persisted.
    """

    # ── 1. Identity lookup ────────────────────────────────────────────────────
    agent = _get_agent(db, from_agent)
    is_known = agent is not None and not agent.is_frozen

    # Frozen agent is treated as unknown
    if agent and agent.is_frozen:
        is_known = False

    # Default policy values for unknown agents
    if is_known and agent:
        policy = _get_policy(db, agent.id)
        allowed_categories = policy.allowed_categories if policy else "gpu_compute,inference"
        daily_limit = policy.daily_limit if policy else 10_000.0
        approval_threshold = policy.approval_threshold if policy else 1_000.0
        max_tx = policy.max_transaction_amount if policy else 5_000.0
        velocity_limit = policy.velocity_limit_per_minute if policy else 40
        rep = agent.reputation_score
        agent_daily_spent = agent.spend_today
        agent_avg = _agent_avg_tx(db, agent.id)
    else:
        allowed_categories = "gpu_compute"
        daily_limit = 0.0
        approval_threshold = 0.0
        max_tx = 0.0
        velocity_limit = 1
        rep = 0.0
        agent_daily_spent = 0.0
        agent_avg = 0.0

    # ── 2. Velocity / RULE 3 ──────────────────────────────────────────────────
    velocity = velocity_service.count_in_window(db, from_agent)
    kill_switch_trigger = is_known and velocity_service.check_kill_switch_threshold(db, from_agent)

    if kill_switch_trigger and not dry_run and agent:
        _freeze_agent(
            db, agent,
            reason=f"Velocity threshold exceeded: {velocity} tx in {60}s window",
            risk_score=0.98,
        )
        db.commit()

    # ── 3. Policy engine ───────────────────────────────────────────────────────
    is_cross_border = currency in ("EUR", "GBP") and from_agent.endswith("-eu")
    decision: PolicyDecision = evaluate(
        from_agent=from_agent,
        to_agent=to_agent,
        amount=amount,
        currency=currency,
        category=category,
        purpose=purpose,
        merchant=merchant,
        allowed_categories_csv=allowed_categories,
        daily_limit=daily_limit,
        approval_threshold=approval_threshold,
        max_transaction_amount=max_tx,
        agent_daily_spent=agent_daily_spent,
        is_known_agent=is_known,
        agent_avg_tx=agent_avg,
        velocity_in_window=velocity,
        velocity_limit=velocity_limit,
        agent_reputation=rep,
        is_cross_border=is_cross_border,
    )

    if dry_run:
        return _build_result(decision, None, from_agent, to_agent, amount, currency, purpose, category, merchant)

    # ── 4. Persist transaction ────────────────────────────────────────────────
    trace_json = json.dumps([
        {"step": t.step, "detail": t.detail, "passed": t.passed}
        for t in decision.policy_trace
    ])

    tx_status = decision.decision
    if tx_status == "human_approval_required":
        tx_status = "escalated"

    display_id = _generate_display_id()
    # Ensure uniqueness
    while db.query(Transaction).filter(Transaction.display_id == display_id).first():
        display_id = _generate_display_id()

    tx = Transaction(
        display_id=display_id,
        agent_id=agent.id if agent else None,
        from_agent=from_agent,
        to_agent=to_agent,
        merchant=merchant or to_agent,
        amount=amount,
        currency=currency,
        purpose=purpose,
        category=category,
        risk_score=decision.risk_score,
        intent_score=decision.intent_score,
        status=tx_status,
        latency_ms=decision.latency_ms,
        policy_trace=trace_json,
    )
    db.add(tx)

    # ── 5. Post-decision side effects ─────────────────────────────────────────
    if decision.decision == "approved":
        if agent:
            agent.spend_today = round(agent.spend_today + amount, 2)
        _update_reputation(db, agent, "approved") if agent else None
        tx.settled_at = datetime.now(timezone.utc)

        # Commit to ledger
        db.flush()  # assign tx.id before ledger entry references it
        ledger_entry = ledger_service.append_entry(db, tx)
        audit_service.log(
            db,
            event_type="TRANSACTION_APPROVED",
            description=f"Approved ${amount:.2f} {currency} from {from_agent} to {to_agent}",
            transaction_id=tx.id,
            agent_id=agent.id if agent else None,
            metadata={"risk_score": decision.risk_score, "latency_ms": decision.latency_ms},
        )
        audit_service.log(
            db,
            event_type="LEDGER_COMMITTED",
            description=f"Ledger entry {ledger_entry.hash[:8]}… committed",
            transaction_id=tx.id,
            agent_id=agent.id if agent else None,
        )

        # Update policy stats
        if is_known and agent:
            pol = _get_policy(db, agent.id)
            if pol:
                pol.triggers += 1

    elif decision.decision == "blocked":
        if agent:
            _update_reputation(db, agent, "blocked")
        audit_service.log(
            db,
            event_type="TRANSACTION_BLOCKED",
            description=f"Blocked ${amount:.2f} {currency} from {from_agent}: {decision.reason}",
            transaction_id=tx.id,
            agent_id=agent.id if agent else None,
            metadata={"reason": decision.reason, "risk_score": decision.risk_score},
        )
        if is_known and agent:
            pol = _get_policy(db, agent.id)
            if pol:
                pol.triggers += 1
                pol.blocks += 1

    else:  # escalated / human_approval_required
        if agent:
            _update_reputation(db, agent, "escalated")
        audit_service.log(
            db,
            event_type="TRANSACTION_ESCALATED",
            description=f"Escalated ${amount:.2f} {currency} from {from_agent}: {decision.reason}",
            transaction_id=tx.id,
            agent_id=agent.id if agent else None,
            metadata={"reason": decision.reason, "risk_score": decision.risk_score},
        )

    db.commit()
    db.refresh(tx)

    return _build_result(decision, tx, from_agent, to_agent, amount, currency, purpose, category, merchant)


def _build_result(
    decision: PolicyDecision,
    tx: Transaction | None,
    from_agent: str,
    to_agent: str,
    amount: float,
    currency: str,
    purpose: str,
    category: str,
    merchant: str,
) -> dict:
    ts = datetime.now(timezone.utc)
    timestamp_str = ts.strftime("%H:%M:%S")

    status = decision.decision
    if status == "human_approval_required":
        status = "escalated"

    return {
        "id": tx.display_id if tx else "dry-run",
        "from": from_agent,
        "to": to_agent,
        "amount": amount,
        "currency": currency,
        "purpose": purpose,
        "category": category,
        "merchant": merchant,
        "status": status,
        "decision": decision.decision,
        "riskScore": decision.risk_score,
        "risk_score": decision.risk_score,
        "intent_score": decision.intent_score,
        "timestamp": timestamp_str,
        "latencyMs": decision.latency_ms,
        "latency_ms": decision.latency_ms,
        "reason": decision.reason,
        "policyTrace": [
            {"step": t.step, "detail": t.detail, "passed": t.passed}
            for t in decision.policy_trace
        ],
        "created_at": ts,
        "transaction_id": tx.id if tx else None,
    }
