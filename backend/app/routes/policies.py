"""
Policy routes.

GET  /policies        List all policies (with agent info)
POST /policies        Create a policy
PUT  /policies/{id}   Update a policy
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent
from app.models.policy import Policy
from app.schemas.policy import PolicyCreateRequest, PolicyUpdateRequest
from app.services import audit_service

router = APIRouter(prefix="/policies", tags=["Policies"])


def _serialize(p: Policy, agent: Agent | None = None) -> dict:
    return {
        "id": p.id,
        "agent_id": p.agent_id,
        "agent_name": agent.name if agent else None,
        "name": p.name,
        "scope": p.scope,
        "daily_limit": p.daily_limit,
        "allowed_categories": p.allowed_categories,
        "max_transaction_amount": p.max_transaction_amount,
        "approval_threshold": p.approval_threshold,
        "velocity_limit_per_minute": p.velocity_limit_per_minute,
        "status": p.status,
        "triggers": p.triggers,
        "blocks": p.blocks,
        "detail": p.detail,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


@router.get("", summary="List all policies")
def list_policies(db: Session = Depends(get_db)):
    policies = db.query(Policy).order_by(Policy.created_at.desc()).all()
    result = []
    for p in policies:
        agent = db.query(Agent).filter(Agent.id == p.agent_id).first()
        result.append(_serialize(p, agent))
    return result


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a policy for an agent")
def create_policy(body: PolicyCreateRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == body.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    policy = Policy(
        agent_id=body.agent_id,
        name=body.name,
        scope=body.scope,
        daily_limit=body.daily_limit,
        allowed_categories=body.allowed_categories,
        max_transaction_amount=body.max_transaction_amount,
        approval_threshold=body.approval_threshold,
        velocity_limit_per_minute=body.velocity_limit_per_minute,
        status=body.status,
        detail=body.detail,
    )
    db.add(policy)

    audit_service.log(
        db,
        event_type="POLICY_CREATED",
        description=f"Policy '{policy.name}' created for agent {agent.name}",
        agent_id=agent.id,
        metadata={"policy_name": policy.name},
    )

    db.commit()
    db.refresh(policy)
    return _serialize(policy, agent)


@router.put("/{policy_id}", summary="Update an existing policy")
def update_policy(policy_id: str, body: PolicyUpdateRequest, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(policy, field, value)

    agent = db.query(Agent).filter(Agent.id == policy.agent_id).first()
    audit_service.log(
        db,
        event_type="POLICY_UPDATED",
        description=f"Policy '{policy.name}' updated",
        agent_id=policy.agent_id,
        metadata=body.model_dump(exclude_none=True),
    )

    db.commit()
    db.refresh(policy)
    return _serialize(policy, agent)
