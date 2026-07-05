"""
Seed data — populates the database on first startup.
Mirrors the frontend mock-data.ts exactly so the UI renders correctly
even before any real transactions flow through.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.audit import AuditLog
from app.models.killswitch import KillSwitchEvent
from app.models.ledger import LedgerEntry
from app.models.policy import Policy
from app.models.transaction import Transaction
from app.models.commerce import ProviderProfile, AutomationWorkflow, NegotiationQuote, WorkflowStep

logger = logging.getLogger(__name__)

# ── Seed agents (mirrors frontend mock-data.ts) ────────────────────────────

_AGENTS = [
    {"name": "openai-buyer-07",   "org": "OpenAI",       "reputation": 99.4, "status": "online",  "spend_today": 42_180.0},
    {"name": "anthropic-broker",  "org": "Anthropic",    "reputation": 98.1, "status": "online",  "spend_today": 31_402.0},
    {"name": "mistral-relayer",   "org": "Mistral",      "reputation": 96.7, "status": "online",  "spend_today": 18_209.0},
    {"name": "llama-compute-4",   "org": "Meta AI",      "reputation": 94.2, "status": "idle",    "spend_today": 9_120.0},
    {"name": "aws-c-broker",      "org": "AWS",          "reputation": 99.8, "status": "online",  "spend_today": 67_902.0},
    {"name": "stripe-relay-01",   "org": "Stripe",       "reputation": 99.9, "status": "online",  "spend_today": 12_500.0},
    {"name": "cohere-embedder-02","org": "Cohere",       "reputation": 80.0, "status": "online",  "spend_today": 0.0},
    {"name": "vertex-inference-eu","org": "Google",      "reputation": 97.3, "status": "online",  "spend_today": 22_100.0},
]

# ── Seed policies ───────────────────────────────────────────────────────────

_POLICY_TEMPLATES = [
    {
        "name": "spend-ceiling-v3",
        "scope": "All agents",
        "daily_limit": 200_000.0,
        "allowed_categories": "gpu_compute,inference,training,data,storage,api,model_weights,embedding",
        "max_transaction_amount": 10_000.0,
        "approval_threshold": 5_000.0,
        "velocity_limit_per_minute": 40,
        "status": "active",
        "triggers": 4128,
        "blocks": 42,
        "detail": "Rolling 1h cap per agent-org pair. Hard block > 3σ deviation from baseline.",
    },
    {
        "name": "eu-cross-border",
        "scope": "EU jurisdiction",
        "daily_limit": 50_000.0,
        "allowed_categories": "gpu_compute,inference,data,api",
        "max_transaction_amount": 10_000.0,
        "approval_threshold": 10_000.0,
        "velocity_limit_per_minute": 20,
        "status": "active",
        "triggers": 892,
        "blocks": 12,
        "detail": "Escalates cross-border settlements > €10k to human on-call for GDPR/PSD3 review.",
    },
    {
        "name": "identity-strict",
        "scope": "All agents",
        "daily_limit": 100_000.0,
        "allowed_categories": "gpu_compute,inference,data,storage,api,model_weights",
        "max_transaction_amount": 5_000.0,
        "approval_threshold": 1_000.0,
        "velocity_limit_per_minute": 40,
        "status": "active",
        "triggers": 19842,
        "blocks": 1204,
        "detail": "Requires mTLS + verifiable credential signed by W3C registry issuer.",
    },
    {
        "name": "velocity-guard",
        "scope": "New agents (< 30d)",
        "daily_limit": 10_000.0,
        "allowed_categories": "gpu_compute,inference,api",
        "max_transaction_amount": 1_000.0,
        "approval_threshold": 500.0,
        "velocity_limit_per_minute": 10,
        "status": "active",
        "triggers": 620,
        "blocks": 88,
        "detail": "Rate-limits new agents to 40 tx / minute until reputation ≥ 90.",
    },
    {
        "name": "org-allowlist",
        "scope": "Enterprise tier",
        "daily_limit": 500_000.0,
        "allowed_categories": "gpu_compute,inference,training,data,storage,api,model_weights,embedding",
        "max_transaction_amount": 50_000.0,
        "approval_threshold": 25_000.0,
        "velocity_limit_per_minute": 100,
        "status": "monitor",
        "triggers": 210,
        "blocks": 0,
        "detail": "Restricts counterparties to explicit allowlist per workspace policy.",
    },
    {
        "name": "anomaly-v2.4",
        "scope": "All agents",
        "daily_limit": 100_000.0,
        "allowed_categories": "gpu_compute,inference,data,storage,api",
        "max_transaction_amount": 5_000.0,
        "approval_threshold": 1_000.0,
        "velocity_limit_per_minute": 40,
        "status": "active",
        "triggers": 30240,
        "blocks": 302,
        "detail": "ML anomaly detector on payload entropy + graph topology. Retrains nightly.",
    },
]

# ── Seed transactions (mirrors frontend mock-data.ts) ──────────────────────

def _ts(minutes_ago: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)


_TRANSACTIONS = [
    {
        "display_id": "0x4f9a2921",
        "from_agent": "openai-buyer-07",
        "to_agent": "aws-c-broker",
        "merchant": "AWS",
        "amount": 1402.0,
        "currency": "USDC",
        "purpose": "H100 GPU lease · 4h",
        "category": "gpu_compute",
        "risk_score": 0.04,
        "intent_score": 96,
        "status": "approved",
        "latency_ms": 11,
        "minutes_ago": 2,
        "policy_trace": [
            {"step": "Identity Verification", "detail": "mTLS + VC signature verified against W3C registry", "passed": True},
            {"step": "Velocity Check", "detail": "Window spend 14% of policy ceiling", "passed": True},
            {"step": "Anomaly Model v2.4", "detail": "Entropy score within expected band", "passed": True},
            {"step": "Settlement", "detail": "Ledger commit 0x4f9a... appended", "passed": True},
        ],
    },
    {
        "display_id": "0x9d3ef42a",
        "from_agent": "anthropic-broker",
        "to_agent": "vertex-inference-eu",
        "merchant": "Google",
        "amount": 890.0,
        "currency": "USD",
        "purpose": "Batch inference · 2.1M tokens",
        "category": "inference",
        "risk_score": 0.11,
        "intent_score": 88,
        "status": "approved",
        "latency_ms": 14,
        "minutes_ago": 3,
        "policy_trace": [
            {"step": "Identity Verification", "detail": "OAuth2 delegated token valid", "passed": True},
            {"step": "Velocity Check", "detail": "Within hourly cap", "passed": True},
            {"step": "Anomaly Model v2.4", "detail": "Nominal", "passed": True},
            {"step": "Settlement", "detail": "Ledger commit appended", "passed": True},
        ],
    },
    {
        "display_id": "0x1a7c1109",
        "from_agent": "unknown-ext-01",
        "to_agent": "compute-cluster-A",
        "merchant": "compute-cluster-A",
        "amount": 50_000.0,
        "currency": "USD",
        "purpose": "Unclassified transfer",
        "category": "unclassified",
        "risk_score": 0.94,
        "intent_score": 4,
        "status": "blocked",
        "latency_ms": 9,
        "minutes_ago": 4,
        "policy_trace": [
            {"step": "Identity Verification", "detail": "Agent not present in registry", "passed": False},
            {"step": "Velocity Check", "detail": "Skipped — identity failure", "passed": False},
            {"step": "Anomaly Model v2.4", "detail": "Amount 42σ above baseline", "passed": False},
            {"step": "Settlement", "detail": "Blocked at gateway", "passed": False},
        ],
    },
    {
        "display_id": "0x77bc21e0",
        "from_agent": "mistral-relayer",
        "to_agent": "stripe-relay-01",
        "merchant": "Stripe",
        "amount": 0.042,
        "currency": "USDC",
        "purpose": "Micro-inference · 1.2k tokens",
        "category": "inference",
        "risk_score": 0.02,
        "intent_score": 96,
        "status": "approved",
        "latency_ms": 8,
        "minutes_ago": 5,
        "policy_trace": [
            {"step": "Identity Verification", "detail": "Verified", "passed": True},
            {"step": "Velocity Check", "detail": "Nominal", "passed": True},
            {"step": "Anomaly Model v2.4", "detail": "Nominal", "passed": True},
            {"step": "Settlement", "detail": "Ledger commit appended", "passed": True},
        ],
    },
    {
        "display_id": "0x21a0b8f4",
        "from_agent": "custom-agent-99",
        "to_agent": "tax-oracle-eu",
        "merchant": "tax-oracle-eu",
        "amount": 458.12,
        "currency": "EUR",
        "purpose": "Tax calculation service",
        "category": "api",
        "risk_score": 0.62,
        "intent_score": 52,
        "status": "escalated",
        "latency_ms": 22,
        "minutes_ago": 6,
        "policy_trace": [
            {"step": "Identity Verification", "detail": "Verified — new agent (48h old)", "passed": True},
            {"step": "Velocity Check", "detail": "First cross-border request", "passed": True},
            {"step": "Anomaly Model v2.4", "detail": "Ambiguous — escalating", "passed": False},
            {"step": "Human Approval", "detail": "Routed to on-call operator", "passed": False},
        ],
    },
    {
        "display_id": "0x55e2a913",
        "from_agent": "llama-compute-4",
        "to_agent": "hf-model-registry",
        "merchant": "HuggingFace",
        "amount": 12.5,
        "currency": "USDC",
        "purpose": "Weights checkpoint pull",
        "category": "model_weights",
        "risk_score": 0.06,
        "intent_score": 90,
        "status": "approved",
        "latency_ms": 12,
        "minutes_ago": 7,
        "policy_trace": [
            {"step": "Identity Verification", "detail": "Verified", "passed": True},
            {"step": "Velocity Check", "detail": "Nominal", "passed": True},
            {"step": "Anomaly Model v2.4", "detail": "Nominal", "passed": True},
            {"step": "Settlement", "detail": "Ledger commit appended", "passed": True},
        ],
    },
    {
        "display_id": "0x88df01ca",
        "from_agent": "openai-buyer-07",
        "to_agent": "pinecone-vector",
        "merchant": "Pinecone",
        "amount": 24.9,
        "currency": "USD",
        "purpose": "Vector index query",
        "category": "embedding",
        "risk_score": 0.03,
        "intent_score": 94,
        "status": "approved",
        "latency_ms": 10,
        "minutes_ago": 8,
        "policy_trace": [
            {"step": "Identity Verification", "detail": "Verified", "passed": True},
            {"step": "Velocity Check", "detail": "Nominal", "passed": True},
            {"step": "Anomaly Model v2.4", "detail": "Nominal", "passed": True},
            {"step": "Settlement", "detail": "Ledger commit appended", "passed": True},
        ],
    },
]


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def run(db: Session) -> None:
    """Idempotent seed — only inserts if tables are empty."""

    # Check if already seeded
    if db.query(Agent).count() > 0:
        logger.info("Database already seeded — skipping")
        return

    logger.info("Seeding database with demo data…")

    # ── 1. Create agents ──────────────────────────────────────────────────────
    agent_map: dict[str, Agent] = {}
    for a_data in _AGENTS:
        agent = Agent(
            id=str(uuid.uuid4()),
            name=a_data["name"],
            org=a_data["org"],
            public_key=f"-----BEGIN PUBLIC KEY-----\n{_sha256(a_data['name'])}\n-----END PUBLIC KEY-----",
            wallet_address=f"0x{_sha256(a_data['name'])[:40]}",
            reputation_score=a_data["reputation"],
            status=a_data["status"],
            spend_today=a_data["spend_today"],
            is_frozen=False,
        )
        db.add(agent)
        agent_map[agent.name] = agent

    db.flush()

    # ── 2. Create policies ────────────────────────────────────────────────────
    # Assign each policy template to the corresponding agent (round-robin for extras)
    main_agents = list(agent_map.values())
    for i, tpl in enumerate(_POLICY_TEMPLATES):
        owner = main_agents[i % len(main_agents)]
        policy = Policy(
            id=str(uuid.uuid4()),
            agent_id=owner.id,
            **{k: v for k, v in tpl.items()},
        )
        db.add(policy)

    # Also create a default policy for every agent that doesn't have one yet
    assigned = set(main_agents[i % len(main_agents)].id for i in range(len(_POLICY_TEMPLATES)))
    for agent in main_agents:
        if agent.id not in assigned:
            db.add(Policy(
                id=str(uuid.uuid4()),
                agent_id=agent.id,
                name="default-policy",
                scope="All agents",
                daily_limit=100_000.0,
                allowed_categories="gpu_compute,inference,data,storage,api,model_weights,embedding",
                max_transaction_amount=5_000.0,
                approval_threshold=1_000.0,
                velocity_limit_per_minute=40,
                status="active",
                detail="Default policy.",
            ))

    db.flush()

    # ── 3. Create transactions ────────────────────────────────────────────────
    previous_hash = "0" * 64
    block_base = 18_200_000

    tx_map: dict[str, Transaction] = {}
    for i, tx_data in enumerate(_TRANSACTIONS):
        created = _ts(tx_data["minutes_ago"])
        agent = agent_map.get(tx_data["from_agent"])

        tx = Transaction(
            id=str(uuid.uuid4()),
            display_id=tx_data["display_id"],
            agent_id=agent.id if agent else None,
            from_agent=tx_data["from_agent"],
            to_agent=tx_data["to_agent"],
            merchant=tx_data["merchant"],
            amount=tx_data["amount"],
            currency=tx_data["currency"],
            purpose=tx_data["purpose"],
            category=tx_data["category"],
            risk_score=tx_data["risk_score"],
            intent_score=tx_data["intent_score"],
            status=tx_data["status"],
            latency_ms=tx_data["latency_ms"],
            policy_trace=json.dumps(tx_data["policy_trace"]),
            created_at=created,
            settled_at=created if tx_data["status"] == "approved" else None,
        )
        db.add(tx)
        tx_map[tx.display_id] = tx

    db.flush()

    # ── 4. Create ledger entries for approved transactions ────────────────────
    for tx in tx_map.values():
        if tx.status != "approved":
            continue
        payload = json.dumps({
            "prev": previous_hash,
            "tx_id": tx.id,
            "display_id": tx.display_id,
            "amount": tx.amount,
            "from": tx.from_agent,
            "to": tx.to_agent,
            "ts": tx.created_at.isoformat() if tx.created_at else "",
        }, sort_keys=True)
        entry_hash = _sha256(payload)
        entry = LedgerEntry(
            id=str(uuid.uuid4()),
            transaction_id=tx.id,
            hash=entry_hash,
            previous_hash=previous_hash,
            block_number=str(block_base + len(tx_map)),
            signer="aether-core-eu-west-1",
            timestamp=tx.created_at or datetime.now(timezone.utc),
        )
        db.add(entry)
        previous_hash = entry_hash

    # ── 5. Seed provider marketplace data ────────────────────────────────────
    providers = [
        {
            "provider_name": "Aether Compute",
            "category": "gpu_compute",
            "region": "us-east-1",
            "price_per_unit": 0.74,
            "sla_days": 3,
            "latency_ms": 38,
            "reputation_score": 99.1,
            "sustainability_score": 95.2,
            "availability": "high",
            "description": "Carbon-aware GPU reserve with fast failover",
        },
        {
            "provider_name": "Nimbus Fabric",
            "category": "inference",
            "region": "eu-west-1",
            "price_per_unit": 0.81,
            "sla_days": 5,
            "latency_ms": 42,
            "reputation_score": 96.8,
            "sustainability_score": 91.4,
            "availability": "medium",
            "description": "Enterprise inference cluster with privacy controls",
        },
        {
            "provider_name": "Helio Grid",
            "category": "training",
            "region": "us-west-2",
            "price_per_unit": 0.77,
            "sla_days": 4,
            "latency_ms": 51,
            "reputation_score": 95.2,
            "sustainability_score": 97.3,
            "availability": "high",
            "description": "Renewable-powered burst training environment",
        },
    ]
    for provider_data in providers:
        db.add(ProviderProfile(**provider_data))

    db.flush()

    workflow = AutomationWorkflow(
        goal="Find a sustainable GPU provider for a training burst",
        amount=125.0,
        currency="USD",
        status="pending_approval",
        workflow_summary="Negotiating GPU burst provider",
        approval_required=True,
    )
    db.add(workflow)
    db.flush()

    for provider in db.query(ProviderProfile).all():
        db.add(
            NegotiationQuote(
                workflow_id=workflow.id,
                provider_id=provider.id,
                provider_name=provider.provider_name,
                price=round(125.0 * provider.price_per_unit, 2),
                sla_days=provider.sla_days,
                latency_ms=provider.latency_ms,
                reputation_score=provider.reputation_score,
                sustainability_score=provider.sustainability_score,
                decision_score=round(provider.reputation_score * 0.4 + provider.sustainability_score * 0.25 + max(0, 100 - provider.latency_ms) * 0.1, 2),
                counter_offer=f"Counter-offer for {provider.provider_name}",
                selected=provider.provider_name == "Aether Compute",
                status="quoted",
            )
        )

    db.add(
        WorkflowStep(
            workflow_id=workflow.id,
            step_name="planner",
            status="completed",
            detail="Goal decomposed into provider discovery and quote evaluation",
        )
    )
    db.add(
        WorkflowStep(
            workflow_id=workflow.id,
            step_name="negotiator",
            status="queued",
            detail="Comparing provider offers",
        )
    )

    # ── 6. Create audit logs ──────────────────────────────────────────────────
    audit_events = [
        {
            "event_type": "TRANSACTION_APPROVED",
            "description": "Settlement batch #4291 finalized · 312 transactions · $184,209 net",
            "dot": "success",
            "minutes_ago": 1,
        },
        {
            "event_type": "POLICY_UPDATED",
            "description": "Policy 'eu-cross-border' triggered · 3 escalations routed to on-call",
            "dot": "warning",
            "minutes_ago": 3,
        },
        {
            "event_type": "AGENT_REGISTERED",
            "description": "New agent onboarded: cohere-embedder-02 · reputation seed 80.0",
            "dot": "primary",
            "minutes_ago": 5,
        },
        {
            "event_type": "TRANSACTION_BLOCKED",
            "description": "Anomaly cluster detected · unknown-ext-01 · $50k blocked",
            "dot": "danger",
            "minutes_ago": 6,
        },
        {
            "event_type": "LEDGER_COMMITTED",
            "description": "Ledger checkpoint anchored · L2 root 0x9c…4a2 · block 18,209,442",
            "dot": "secondary",
            "minutes_ago": 10,
        },
    ]
    for ev in audit_events:
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            event_type=ev["event_type"],
            description=ev["description"],
            dot=ev["dot"],
            timestamp=_ts(ev["minutes_ago"]),
        ))

    db.commit()
    logger.info("Seed complete — %d agents, %d transactions loaded", len(agent_map), len(tx_map))
