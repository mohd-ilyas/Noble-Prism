"""
Pydantic v2 schemas for the Insights / Analytics endpoint.
"""
from __future__ import annotations

from pydantic import BaseModel


class VolumeSeries(BaseModel):
    """One hour's authorized/blocked counts — matches frontend volumeSeries shape."""
    hour: str       # e.g. "14:00"
    authorized: int
    blocked: int


class KpiData(BaseModel):
    authorized_volume: float
    blocked_requests: int
    avg_latency_ms: float
    active_agents: int


class InsightItem(BaseModel):
    tone: str        # danger | primary | secondary | success
    title: str
    body: str
    action: str


class EventItem(BaseModel):
    kind: str
    title: str
    detail: str
    dot: str         # success | warning | danger | primary | secondary


class InsightsResponse(BaseModel):
    kpis: KpiData
    volume_series: list[VolumeSeries]
    insights: list[InsightItem]
    events: list[EventItem]
