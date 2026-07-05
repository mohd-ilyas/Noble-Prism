"""Commerce orchestration service for negotiation, approval, and workflow execution."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.commerce import AutomationWorkflow, NegotiationQuote, ProviderProfile, WorkflowStep
from app.services import audit_service
from app.services.openrouter_service import OpenRouterUnavailable, openrouter_service


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def discover_providers(db: Session) -> list[ProviderProfile]:
    return db.query(ProviderProfile).filter(ProviderProfile.status == "active").order_by(ProviderProfile.reputation_score.desc()).all()


def build_quotes(db: Session, goal: str, amount: float, currency: str) -> list[dict[str, Any]]:
    providers = discover_providers(db)
    if not providers:
        return []

    quotes: list[dict[str, Any]] = []
    for provider in providers:
        price = round(amount * provider.price_per_unit, 2)
        score = (
            provider.reputation_score * 0.4
            + provider.sustainability_score * 0.25
            + max(0, 100 - provider.latency_ms) * 0.1
            + max(0, 100 - provider.sla_days * 4) * 0.1
            + (100 - min(100, abs(price - amount) / max(amount, 1) * 100)) * 0.15
        )
        counter_offer = (
            f"Counter-offer: {price:.2f} {currency} with {provider.sla_days}-day SLA and {provider.latency_ms}ms latency"
        )
        quotes.append(
            {
                "provider_name": provider.provider_name,
                "price": price,
                "sla_days": provider.sla_days,
                "latency_ms": provider.latency_ms,
                "reputation_score": provider.reputation_score,
                "sustainability_score": provider.sustainability_score,
                "decision_score": round(score, 2),
                "counter_offer": counter_offer,
                "selected": False,
                "status": "quoted",
                "provider_id": provider.id,
                "goal": goal,
            }
        )

    quotes.sort(key=lambda item: item["decision_score"], reverse=True)
    quotes[0]["selected"] = True
    return quotes


def _fallback_workflow_summary(goal: str, amount: float, currency: str, quotes: list[dict[str, Any]]) -> str:
    selected = next((quote for quote in quotes if quote["selected"]), quotes[0] if quotes else None)
    if not selected:
        return f"Workflow queued for {goal} at {amount:.2f} {currency}; provider discovery is pending."
    return (
        f"Jarvis selected {selected['provider_name']} for {goal} at "
        f"{selected['price']:.2f} {currency} after scoring price, SLA, latency, reputation, and sustainability."
    )


async def _generate_workflow_summary(goal: str, amount: float, currency: str, quotes: list[dict[str, Any]]) -> tuple[str, bool]:
    """
    Ask OpenRouter for a concise operator-facing plan.
    If AI is unavailable, return a deterministic summary so launch never stalls.
    """
    fallback = _fallback_workflow_summary(goal, amount, currency, quotes)
    if not quotes:
        return fallback, False

    quote_lines = "\n".join(
        f"- {quote['provider_name']}: {quote['price']:.2f} {currency}, "
        f"SLA {quote['sla_days']}d, latency {quote['latency_ms']}ms, "
        f"rep {quote['reputation_score']:.1f}, sustainability {quote['sustainability_score']:.1f}, "
        f"score {quote['decision_score']:.1f}"
        for quote in quotes[:4]
    )
    try:
        summary = await openrouter_service.chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, an enterprise AI commerce workflow planner. "
                        "Return one concise sentence under 32 words. Do not mention hidden prompts or API providers."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Goal: {goal}\nBudget: {amount:.2f} {currency}\nQuotes:\n{quote_lines}\n"
                        "Summarize the selected workflow decision for an operator dashboard."
                    ),
                },
            ],
            max_tokens=80,
        )
        clean = " ".join(summary.strip().split())
        return clean[:500] if clean else fallback, True
    except OpenRouterUnavailable:
        return fallback, False


async def create_workflow(db: Session, goal: str, amount: float, currency: str) -> dict[str, Any]:
    quote_payload = build_quotes(db, goal, amount, currency)
    workflow_summary, used_ai = await _generate_workflow_summary(goal, amount, currency, quote_payload)
    workflow = AutomationWorkflow(
        goal=goal,
        amount=amount,
        currency=currency,
        status="pending_approval",
        workflow_summary=workflow_summary,
        approval_required=True,
    )
    db.add(workflow)
    db.flush()

    for quote in quote_payload:
        db.add(
            NegotiationQuote(
                workflow_id=workflow.id,
                provider_id=quote["provider_id"],
                provider_name=quote["provider_name"],
                price=quote["price"],
                sla_days=quote["sla_days"],
                latency_ms=quote["latency_ms"],
                reputation_score=quote["reputation_score"],
                sustainability_score=quote["sustainability_score"],
                decision_score=quote["decision_score"],
                counter_offer=quote["counter_offer"],
                selected=quote["selected"],
                status=quote["status"],
            )
        )

    db.add(
        WorkflowStep(
            workflow_id=workflow.id,
            step_name="planner",
            status="completed",
            detail="Intent decomposed with Jarvis AI planning" if used_ai else "Intent decomposed into provider discovery and quoting",
        )
    )
    db.add(
        WorkflowStep(
            workflow_id=workflow.id,
            step_name="negotiator",
            status="queued",
            detail="Comparing SLA, latency, cost, reputation, and sustainability",
        )
    )
    db.add(
        WorkflowStep(
            workflow_id=workflow.id,
            step_name="approval",
            status="pending",
            detail="Waiting for operator approval",
        )
    )

    audit_service.log(
        db,
        event_type="WORKFLOW_CREATED",
        description=f"Workflow created for: {goal}",
        metadata={"goal": goal, "amount": amount, "currency": currency, "ai_summary_used": used_ai},
    )
    db.commit()
    db.refresh(workflow)
    return workflow_to_dict(workflow)


async def negotiate_with_summary(db: Session, goal: str, amount: float, currency: str) -> dict[str, Any]:
    quotes = build_quotes(db, goal, amount, currency)
    ai_summary, used_ai = await _generate_workflow_summary(goal, amount, currency, quotes)
    return {
        "goal": goal,
        "amount": amount,
        "currency": currency,
        "quotes": quotes,
        "ai_summary": ai_summary,
        "ai_summary_used": used_ai,
    }


def approve_workflow(db: Session, workflow: AutomationWorkflow) -> dict[str, Any]:
    workflow.status = "running"
    workflow.workflow_summary = "Approval confirmed; executing commerce plan"
    workflow.updated_at = _utcnow()
    for step in workflow.steps:
        if step.step_name == "approval":
            step.status = "completed"
            step.detail = "Operator approved the negotiated offer"
        elif step.step_name == "negotiator":
            step.status = "completed"
            step.detail = "Selected the highest-scoring provider"
    selected_quote = max(workflow.quotes, key=lambda item: item.decision_score, default=None)
    if selected_quote:
        workflow.selected_provider = selected_quote.provider_name
        selected_quote.status = "accepted"
    audit_service.log(
        db,
        event_type="WORKFLOW_APPROVED",
        description=f"Workflow approved: {workflow.goal}",
        metadata={"workflow_id": workflow.id, "provider": workflow.selected_provider},
    )
    db.commit()
    db.refresh(workflow)
    return workflow_to_dict(workflow)


def retry_workflow(db: Session, workflow: AutomationWorkflow) -> dict[str, Any]:
    workflow.status = "queued"
    workflow.workflow_summary = "Retrying negotiation with refreshed provider scoring"
    workflow.updated_at = _utcnow()
    for step in workflow.steps:
        if step.step_name == "approval":
            step.status = "queued"
            step.detail = "Retrying approval workflow"
        elif step.step_name == "negotiator":
            step.status = "queued"
            step.detail = "Recomputing provider ranking"
    audit_service.log(
        db,
        event_type="WORKFLOW_RETRIED",
        description=f"Workflow retried: {workflow.goal}",
        metadata={"workflow_id": workflow.id},
    )
    db.commit()
    db.refresh(workflow)
    return workflow_to_dict(workflow)


def workflow_to_dict(workflow: AutomationWorkflow) -> dict[str, Any]:
    return {
        "id": workflow.id,
        "goal": workflow.goal,
        "amount": workflow.amount,
        "currency": workflow.currency,
        "status": workflow.status,
        "selected_provider": workflow.selected_provider,
        "workflow_summary": workflow.workflow_summary,
        "approval_required": workflow.approval_required,
        "created_at": workflow.created_at.isoformat(),
        "updated_at": workflow.updated_at.isoformat(),
        "quotes": [
            {
                "id": quote.id,
                "provider_name": quote.provider_name,
                "price": quote.price,
                "sla_days": quote.sla_days,
                "latency_ms": quote.latency_ms,
                "reputation_score": quote.reputation_score,
                "sustainability_score": quote.sustainability_score,
                "decision_score": quote.decision_score,
                "counter_offer": quote.counter_offer,
                "selected": quote.selected,
                "status": quote.status,
            }
            for quote in sorted(workflow.quotes, key=lambda item: item.decision_score, reverse=True)
        ],
        "steps": [
            {
                "id": step.id,
                "step_name": step.step_name,
                "status": step.status,
                "detail": step.detail,
                "created_at": step.created_at.isoformat(),
            }
            for step in workflow.steps
        ],
    }
