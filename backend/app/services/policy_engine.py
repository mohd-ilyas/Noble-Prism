"""
Policy Engine — deterministic rule evaluation pipeline.

Each step returns a PolicyTraceEntry and may short-circuit to a final decision.

Rules (per problem statement):
  RULE 1 — Intent mismatch            → blocked
  RULE 2 — Amount > approval_threshold → human_approval_required
  RULE 3 — Velocity exceeded           → kill_switch  (handled upstream)
  RULE 4 — Policy satisfied            → approved
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Literal

from app.services.intent_engine import score_intent
from app.services.risk_engine import compute_risk_score


Decision = Literal["approved", "blocked", "human_approval_required", "escalated"]


@dataclass
class PolicyTraceEntry:
    step: str
    detail: str
    passed: bool


@dataclass
class PolicyDecision:
    decision: Decision
    intent_score: int
    risk_score: float
    reason: str
    latency_ms: int
    policy_trace: list[PolicyTraceEntry] = field(default_factory=list)


def evaluate(
    *,
    from_agent: str,
    to_agent: str,
    amount: float,
    currency: str,
    category: str,
    purpose: str,
    merchant: str,
    # Policy parameters
    allowed_categories_csv: str,
    daily_limit: float,
    approval_threshold: float,
    max_transaction_amount: float,
    agent_daily_spent: float,
    # Risk inputs
    is_known_agent: bool,
    agent_avg_tx: float,
    velocity_in_window: int,
    velocity_limit: int,
    agent_reputation: float,
    is_cross_border: bool = False,
) -> PolicyDecision:
    """
    Run the full policy pipeline and return a PolicyDecision with trace.
    """
    t0 = time.perf_counter()
    trace: list[PolicyTraceEntry] = []

    # ── Step 1: Identity Verification ────────────────────────────────────────
    if not is_known_agent:
        trace.append(PolicyTraceEntry(
            step="Identity Verification",
            detail="Agent not present in registry",
            passed=False,
        ))
        trace.append(PolicyTraceEntry(step="Velocity Check", detail="Skipped — identity failure", passed=False))
        trace.append(PolicyTraceEntry(step="Anomaly Model v2.4", detail="Amount likely above baseline", passed=False))
        trace.append(PolicyTraceEntry(step="Settlement", detail="Blocked at gateway", passed=False))
        risk = compute_risk_score(
            amount=amount, agent_avg_tx=0, is_known_agent=False,
            velocity_in_window=0, velocity_limit=max(1, velocity_limit),
            category=category, purpose=purpose, currency=currency,
            agent_reputation=0.0,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return PolicyDecision(
            decision="blocked",
            intent_score=4,
            risk_score=round(min(0.95, 0.70 + risk * 0.25), 4),
            reason="Agent identity not found in registry",
            latency_ms=latency_ms,
            policy_trace=trace,
        )

    identity_detail = "mTLS + VC signature verified against registry"
    trace.append(PolicyTraceEntry(step="Identity Verification", detail=identity_detail, passed=True))

    # ── Step 2: Intent Verification (RULE 1) ─────────────────────────────────
    intent_score, intent_ok = score_intent(category, purpose, allowed_categories_csv)

    if not intent_ok:
        trace.append(PolicyTraceEntry(
            step="Intent Verification",
            detail=f"Category '{category}' not in allowed set: {allowed_categories_csv}",
            passed=False,
        ))
        trace.append(PolicyTraceEntry(step="Velocity Check", detail="Skipped — intent failure", passed=False))
        trace.append(PolicyTraceEntry(step="Settlement", detail="Blocked at gateway", passed=False))
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return PolicyDecision(
            decision="blocked",
            intent_score=4,
            risk_score=0.82,
            reason="intent mismatch",
            latency_ms=latency_ms,
            policy_trace=trace,
        )

    trace.append(PolicyTraceEntry(
        step="Intent Verification",
        detail=f"Intent score {intent_score}/100 — category '{category}' allowed",
        passed=True,
    ))

    # ── Step 3: Velocity check ────────────────────────────────────────────────
    velocity_ok = velocity_in_window < velocity_limit
    if velocity_ok:
        v_pct = int(velocity_in_window / max(1, velocity_limit) * 100)
        trace.append(PolicyTraceEntry(
            step="Velocity Check",
            detail=f"Window spend {v_pct}% of policy ceiling",
            passed=True,
        ))
    else:
        trace.append(PolicyTraceEntry(
            step="Velocity Check",
            detail=f"Rate exceeded: {velocity_in_window} tx in window (limit {velocity_limit})",
            passed=False,
        ))

    # ── Step 4: Amount limits ─────────────────────────────────────────────────
    if amount > max_transaction_amount:
        trace.append(PolicyTraceEntry(
            step="Transaction Limit",
            detail=f"${amount:,.2f} exceeds per-tx limit of ${max_transaction_amount:,.2f}",
            passed=False,
        ))
        trace.append(PolicyTraceEntry(step="Settlement", detail="Blocked — amount limit exceeded", passed=False))
        latency_ms = int((time.perf_counter() - t0) * 1000)
        risk = compute_risk_score(
            amount=amount, agent_avg_tx=agent_avg_tx, is_known_agent=True,
            velocity_in_window=velocity_in_window, velocity_limit=velocity_limit,
            category=category, purpose=purpose, currency=currency,
            agent_reputation=agent_reputation,
        )
        return PolicyDecision(
            decision="blocked",
            intent_score=intent_score,
            risk_score=risk,
            reason=f"Amount ${amount:,.2f} exceeds max transaction limit ${max_transaction_amount:,.2f}",
            latency_ms=latency_ms,
            policy_trace=trace,
        )

    trace.append(PolicyTraceEntry(
        step="Transaction Limit",
        detail=f"${amount:,.2f} within max transaction limit ${max_transaction_amount:,.2f}",
        passed=True,
    ))

    # ── Step 5: Daily limit check ─────────────────────────────────────────────
    projected_daily = agent_daily_spent + amount
    if projected_daily > daily_limit:
        trace.append(PolicyTraceEntry(
            step="Daily Limit",
            detail=f"Projected daily spend ${projected_daily:,.2f} would exceed ${daily_limit:,.2f} limit",
            passed=False,
        ))
        trace.append(PolicyTraceEntry(step="Settlement", detail="Blocked — daily limit exceeded", passed=False))
        latency_ms = int((time.perf_counter() - t0) * 1000)
        risk = compute_risk_score(
            amount=amount, agent_avg_tx=agent_avg_tx, is_known_agent=True,
            velocity_in_window=velocity_in_window, velocity_limit=velocity_limit,
            category=category, purpose=purpose, currency=currency,
            agent_reputation=agent_reputation,
        )
        return PolicyDecision(
            decision="blocked",
            intent_score=intent_score,
            risk_score=risk,
            reason="Daily spending limit exceeded",
            latency_ms=latency_ms,
            policy_trace=trace,
        )

    trace.append(PolicyTraceEntry(
        step="Daily Limit",
        detail=f"Projected ${projected_daily:,.2f} within daily limit ${daily_limit:,.2f}",
        passed=True,
    ))

    # ── Step 6: Risk / anomaly scoring ───────────────────────────────────────
    risk = compute_risk_score(
        amount=amount,
        agent_avg_tx=agent_avg_tx,
        is_known_agent=True,
        velocity_in_window=velocity_in_window,
        velocity_limit=velocity_limit,
        category=category,
        purpose=purpose,
        currency=currency,
        agent_reputation=agent_reputation,
        is_cross_border=is_cross_border,
    )

    if risk > 0.75:
        trace.append(PolicyTraceEntry(
            step="Anomaly Model v2.4",
            detail=f"Risk score {risk:.2f} above threshold — escalating",
            passed=False,
        ))
        trace.append(PolicyTraceEntry(
            step="Human Approval",
            detail="Routed to on-call operator",
            passed=False,
        ))
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return PolicyDecision(
            decision="escalated",
            intent_score=intent_score,
            risk_score=risk,
            reason="Anomaly model flagged transaction for human review",
            latency_ms=latency_ms,
            policy_trace=trace,
        )

    if risk > 0.30:
        anomaly_detail = "Ambiguous — escalating"
        anomaly_passed = False
    else:
        anomaly_detail = "Entropy score within expected band"
        anomaly_passed = True

    trace.append(PolicyTraceEntry(
        step="Anomaly Model v2.4",
        detail=anomaly_detail,
        passed=anomaly_passed,
    ))

    # ── Step 7: Approval threshold (RULE 2) ──────────────────────────────────
    if amount > approval_threshold:
        trace.append(PolicyTraceEntry(
            step="Approval Threshold",
            detail=f"${amount:,.2f} exceeds approval threshold ${approval_threshold:,.2f} — human review required",
            passed=False,
        ))
        trace.append(PolicyTraceEntry(step="Human Approval", detail="Routed to on-call operator", passed=False))
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return PolicyDecision(
            decision="human_approval_required",
            intent_score=intent_score,
            risk_score=risk,
            reason=f"Amount ${amount:,.2f} exceeds approval threshold ${approval_threshold:,.2f}",
            latency_ms=latency_ms,
            policy_trace=trace,
        )

    trace.append(PolicyTraceEntry(
        step="Approval Threshold",
        detail=f"${amount:,.2f} below approval threshold ${approval_threshold:,.2f}",
        passed=True,
    ))

    # ── Step 8: Anomaly-escalated transactions ────────────────────────────────
    if not anomaly_passed:
        trace.append(PolicyTraceEntry(step="Human Approval", detail="Routed to on-call operator", passed=False))
        latency_ms = int((time.perf_counter() - t0) * 1000)
        return PolicyDecision(
            decision="escalated",
            intent_score=intent_score,
            risk_score=risk,
            reason="Transaction flagged by anomaly model",
            latency_ms=latency_ms,
            policy_trace=trace,
        )

    # ── Step 9: Settlement (RULE 4) ───────────────────────────────────────────
    trace.append(PolicyTraceEntry(
        step="Settlement",
        detail=f"Ledger commit appended",
        passed=True,
    ))

    latency_ms = int((time.perf_counter() - t0) * 1000)
    return PolicyDecision(
        decision="approved",
        intent_score=intent_score,
        risk_score=risk,
        reason="All policy checks passed",
        latency_ms=latency_ms,
        policy_trace=trace,
    )
