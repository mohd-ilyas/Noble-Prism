"""
Pydantic v2 schemas for Policy.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PolicyCreateRequest(BaseModel):
    agent_id: str
    name: str = Field(default="default-policy", max_length=128)
    scope: str = Field(default="All agents", max_length=128)
    daily_limit: float = Field(default=100_000.0, gt=0)
    allowed_categories: str = Field(default="gpu_compute,inference,data,storage,api")
    max_transaction_amount: float = Field(default=5_000.0, gt=0)
    approval_threshold: float = Field(default=1_000.0, gt=0)
    velocity_limit_per_minute: int = Field(default=40, gt=0)
    status: str = Field(default="active")
    detail: str = Field(default="")


class PolicyUpdateRequest(BaseModel):
    name: Optional[str] = None
    scope: Optional[str] = None
    daily_limit: Optional[float] = None
    allowed_categories: Optional[str] = None
    max_transaction_amount: Optional[float] = None
    approval_threshold: Optional[float] = None
    velocity_limit_per_minute: Optional[int] = None
    status: Optional[str] = None
    detail: Optional[str] = None


class PolicyResponse(BaseModel):
    id: str
    agent_id: str
    name: str
    scope: str
    daily_limit: float
    allowed_categories: str
    max_transaction_amount: float
    approval_threshold: float
    velocity_limit_per_minute: int
    status: str
    triggers: int
    blocks: int
    detail: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
