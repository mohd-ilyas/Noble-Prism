"""
Pydantic v2 schemas for Agent — request/response shapes that match
the frontend's Agent interface exactly.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AgentRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    org: str = Field(default="Unknown", max_length=128)
    public_key: str = Field(..., min_length=1)
    wallet_address: str = Field(..., min_length=1, max_length=64)


class AgentResponse(BaseModel):
    id: str
    name: str
    org: str
    public_key: str
    wallet_address: str
    reputation_score: float
    # Frontend calls this field 'reputation'
    reputation: float
    status: str
    spend_today: float
    # Frontend also uses camelCase 'spendToday'
    spendToday: float
    is_frozen: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_agent(cls, agent) -> "AgentResponse":
        return cls(
            id=agent.id,
            name=agent.name,
            org=agent.org,
            public_key=agent.public_key,
            wallet_address=agent.wallet_address,
            reputation_score=agent.reputation_score,
            reputation=agent.reputation_score,
            status=agent.status,
            spend_today=agent.spend_today,
            spendToday=agent.spend_today,
            is_frozen=agent.is_frozen,
            created_at=agent.created_at,
        )
