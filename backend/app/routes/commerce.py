"""Commerce routes for negotiation, workflow management, and live updates."""
from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.commerce import AutomationWorkflow, ProviderProfile
from app.schemas.commerce import WorkflowCreateRequest, WorkflowResponse
from app.services import commerce_service

router = APIRouter(prefix="/commerce", tags=["Commerce"])


@router.get("/providers", summary="List available providers")
def list_providers(db: Session = Depends(get_db)):
    providers = commerce_service.discover_providers(db)
    return [
        {
            "id": provider.id,
            "provider_name": provider.provider_name,
            "category": provider.category,
            "region": provider.region,
            "price_per_unit": provider.price_per_unit,
            "sla_days": provider.sla_days,
            "latency_ms": provider.latency_ms,
            "reputation_score": provider.reputation_score,
            "sustainability_score": provider.sustainability_score,
            "availability": provider.availability,
            "description": provider.description,
            "status": provider.status,
        }
        for provider in providers
    ]


@router.get("/providers/{provider_id}", summary="Fetch one provider")
def get_provider(provider_id: str, db: Session = Depends(get_db)):
    provider = db.query(ProviderProfile).filter(ProviderProfile.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {
        "id": provider.id,
        "provider_name": provider.provider_name,
        "category": provider.category,
        "region": provider.region,
        "price_per_unit": provider.price_per_unit,
        "sla_days": provider.sla_days,
        "latency_ms": provider.latency_ms,
        "reputation_score": provider.reputation_score,
        "sustainability_score": provider.sustainability_score,
        "availability": provider.availability,
        "description": provider.description,
        "status": provider.status,
    }


@router.post("/negotiations", summary="Discover providers and request quotes")
async def negotiate(body: WorkflowCreateRequest, db: Session = Depends(get_db)):
    return await commerce_service.negotiate_with_summary(db, body.goal, body.amount, body.currency)


@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED, summary="Create a new automation workflow")
async def create_workflow(body: WorkflowCreateRequest, db: Session = Depends(get_db)):
    return await commerce_service.create_workflow(db, body.goal, body.amount, body.currency)


@router.get("/workflows", response_model=list[WorkflowResponse], summary="List workflows")
def list_workflows(db: Session = Depends(get_db)):
    workflows = db.query(AutomationWorkflow).order_by(AutomationWorkflow.created_at.desc()).all()
    return [commerce_service.workflow_to_dict(workflow) for workflow in workflows]


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse, summary="Get workflow")
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    workflow = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return commerce_service.workflow_to_dict(workflow)


@router.get("/workflows/{workflow_id}/quotes", summary="List workflow quotes")
def list_workflow_quotes(workflow_id: str, db: Session = Depends(get_db)):
    workflow = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return [
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
    ]


@router.post("/workflows/{workflow_id}/approve", response_model=WorkflowResponse, summary="Approve a pending workflow")
def approve_workflow(workflow_id: str, db: Session = Depends(get_db)):
    workflow = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return commerce_service.approve_workflow(db, workflow)


@router.post("/workflows/{workflow_id}/retry", response_model=WorkflowResponse, summary="Retry a workflow")
def retry_workflow(workflow_id: str, db: Session = Depends(get_db)):
    workflow = db.query(AutomationWorkflow).filter(AutomationWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return commerce_service.retry_workflow(db, workflow)


def _simulate_provider_update(provider: ProviderProfile, seed: int) -> dict[str, object]:
    def clamp(value: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(value, max_value))

    price = clamp(provider.price_per_unit * (1 + random.uniform(-0.08, 0.08)), 0.1, 9999)
    sla_days = clamp(provider.sla_days + random.uniform(-0.65, 0.65), 1, 30)
    latency_ms = clamp(provider.latency_ms + random.uniform(-12, 12), 1, 250)
    reputation_score = clamp(provider.reputation_score + random.uniform(-1.5, 1.5), 0, 100)
    sustainability_score = clamp(provider.sustainability_score + random.uniform(-1.5, 1.5), 0, 100)
    availability = provider.availability
    if random.random() < 0.18:
        availability = "high" if availability != "high" else "medium"
    if random.random() < 0.08:
        availability = "low"

    return {
        "id": provider.id,
        "provider_name": provider.provider_name,
        "category": provider.category,
        "region": provider.region,
        "price_per_unit": round(price, 2),
        "sla_days": round(sla_days, 1),
        "latency_ms": round(latency_ms),
        "reputation_score": round(reputation_score, 1),
        "sustainability_score": round(sustainability_score, 1),
        "availability": availability,
        "description": provider.description,
        "status": provider.status,
    }


@router.websocket("/ws")
async def commerce_ws(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        await websocket.send_json({"type": "connected", "message": "Commerce stream connected"})
        while True:
            providers = commerce_service.discover_providers(db)
            workflows = db.query(AutomationWorkflow).order_by(AutomationWorkflow.created_at.desc()).limit(3).all()

            await websocket.send_json(
                {
                    "type": "commerce_snapshot",
                    "message": "Live commerce snapshot",
                    "payload": {
                        "providers": [
                            _simulate_provider_update(provider, idx)
                            for idx, provider in enumerate(providers)
                        ],
                        "workflows": [commerce_service.workflow_to_dict(workflow) for workflow in workflows],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                }
            )
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        return
