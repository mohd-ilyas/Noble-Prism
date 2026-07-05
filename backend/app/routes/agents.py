"""
Agent routes — identity and wallet management.

GET  /agents            List all agents
POST /agents/register   Register a new agent
GET  /agents/{id}       Get a single agent by ID or name
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent
from app.models.policy import Policy
from app.schemas.agent import AgentRegisterRequest, AgentResponse
from app.services import audit_service

router = APIRouter(prefix="/agents", tags=["Agents"])


def _serialize(agent: Agent) -> dict:
    return {
        "id": agent.id,
        "name": agent.name,
        "org": agent.org,
        "public_key": agent.public_key,
        "wallet_address": agent.wallet_address,
        "reputation_score": agent.reputation_score,
        "reputation": agent.reputation_score,   # frontend alias
        "status": agent.status,
        "spend_today": agent.spend_today,
        "spendToday": agent.spend_today,          # frontend alias
        "is_frozen": agent.is_frozen,
        "created_at": agent.created_at,
    }


@router.get("", summary="List all registered agents")
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).order_by(Agent.reputation_score.desc()).all()
    return [_serialize(a) for a in agents]


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new agent")
def register_agent(body: AgentRegisterRequest, db: Session = Depends(get_db)):
    # Check uniqueness
    existing = db.query(Agent).filter(
        (Agent.name == body.name) | (Agent.wallet_address == body.wallet_address)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Agent name or wallet address already registered",
        )

    agent = Agent(
        name=body.name,
        org=body.org,
        public_key=body.public_key,
        wallet_address=body.wallet_address,
        reputation_score=80.0,
        status="online",
    )
    db.add(agent)
    db.flush()

    # Create a default policy for the agent
    default_policy = Policy(
        agent_id=agent.id,
        name="default-policy",
        scope="All agents",
        daily_limit=100_000.0,
        allowed_categories="gpu_compute,inference,data,storage,api",
        max_transaction_amount=5_000.0,
        approval_threshold=1_000.0,
        velocity_limit_per_minute=40,
        status="active",
        detail="Default policy auto-generated at registration.",
    )
    db.add(default_policy)

    audit_service.log(
        db,
        event_type="AGENT_REGISTERED",
        description=f"New agent registered: {agent.name} ({agent.org})",
        agent_id=agent.id,
    )

    db.commit()
    db.refresh(agent)
    return _serialize(agent)


@router.get("/{agent_id}", summary="Get agent by ID or name")
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = (
        db.query(Agent)
        .filter((Agent.id == agent_id) | (Agent.name == agent_id))
        .first()
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _serialize(agent)
