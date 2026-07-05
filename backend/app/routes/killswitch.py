"""
Kill-switch routes.

POST /killswitch/activate   Manually freeze an agent
POST /killswitch/release    Release a frozen agent
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent
from app.models.killswitch import KillSwitchEvent
from app.services import audit_service

router = APIRouter(prefix="/killswitch", tags=["Kill Switch"])


class ActivateRequest(BaseModel):
    agent_id: str
    reason: str = Field(..., min_length=1)
    risk_score: float = Field(default=0.99, ge=0.0, le=1.0)


class ReleaseRequest(BaseModel):
    agent_id: str
    note: str = Field(default="")


@router.post("/activate", summary="Freeze an agent — blocks all future transactions")
def activate_kill_switch(body: ActivateRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(
        (Agent.id == body.agent_id) | (Agent.name == body.agent_id)
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.is_frozen = True
    agent.status = "offline"

    ks = KillSwitchEvent(
        agent_id=agent.id,
        reason=body.reason,
        risk_score=body.risk_score,
        triggered_by="human",
    )
    db.add(ks)

    audit_service.log(
        db,
        event_type="KILL_SWITCH_ACTIVATED",
        description=f"Kill switch activated for {agent.name}: {body.reason}",
        agent_id=agent.id,
        metadata={"risk_score": body.risk_score, "triggered_by": "human"},
    )

    db.commit()
    db.refresh(ks)

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "reason": ks.reason,
        "risk_score": ks.risk_score,
        "triggered_at": ks.triggered_at,
        "released_at": ks.released_at,
        "status": "active",
    }


@router.post("/release", summary="Release a frozen agent")
def release_kill_switch(body: ReleaseRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(
        (Agent.id == body.agent_id) | (Agent.name == body.agent_id)
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not agent.is_frozen:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Agent is not currently frozen",
        )

    agent.is_frozen = False
    agent.status = "online"

    # Mark most recent active kill-switch event as released
    active_ks = (
        db.query(KillSwitchEvent)
        .filter(KillSwitchEvent.agent_id == agent.id, KillSwitchEvent.released_at.is_(None))
        .order_by(KillSwitchEvent.triggered_at.desc())
        .first()
    )
    if active_ks:
        active_ks.released_at = datetime.now(timezone.utc)

    audit_service.log(
        db,
        event_type="KILL_SWITCH_RELEASED",
        description=f"Kill switch released for {agent.name}. Note: {body.note}",
        agent_id=agent.id,
        metadata={"note": body.note},
    )

    db.commit()

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "status": "released",
        "released_at": active_ks.released_at if active_ks else datetime.now(timezone.utc),
        "message": f"Agent {agent.name} is now active",
    }


@router.get("", summary="List all kill-switch events")
def list_kill_switch_events(db: Session = Depends(get_db)):
    events = (
        db.query(KillSwitchEvent)
        .order_by(KillSwitchEvent.triggered_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": e.id,
            "agent_id": e.agent_id,
            "reason": e.reason,
            "risk_score": e.risk_score,
            "triggered_by": e.triggered_by,
            "triggered_at": e.triggered_at,
            "released_at": e.released_at,
            "status": "released" if e.released_at else "active",
        }
        for e in events
    ]
