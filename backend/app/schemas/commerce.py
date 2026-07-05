from __future__ import annotations

from pydantic import BaseModel, Field


class ProviderResponse(BaseModel):
    id: str
    provider_name: str
    category: str
    region: str
    price_per_unit: float
    sla_days: int
    latency_ms: int
    reputation_score: float
    sustainability_score: float
    availability: str
    description: str
    status: str


class WorkflowCreateRequest(BaseModel):
    goal: str = Field(..., min_length=3)
    amount: float = Field(default=100.0, ge=0)
    currency: str = Field(default="USD")


class WorkflowStepResponse(BaseModel):
    id: str
    step_name: str
    status: str
    detail: str
    created_at: str


class QuoteResponse(BaseModel):
    id: str
    provider_name: str
    price: float
    sla_days: int
    latency_ms: int
    reputation_score: float
    sustainability_score: float
    decision_score: float
    counter_offer: str
    selected: bool
    status: str


class WorkflowResponse(BaseModel):
    id: str
    goal: str
    amount: float
    currency: str
    status: str
    selected_provider: str | None = None
    workflow_summary: str
    approval_required: bool
    created_at: str
    updated_at: str
    quotes: list[QuoteResponse]
    steps: list[WorkflowStepResponse]
