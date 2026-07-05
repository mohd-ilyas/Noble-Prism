"""Commerce and automation models for the autonomous AI commerce OS."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProviderProfile(Base):
    __tablename__ = "provider_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="compute")
    region: Mapped[str] = mapped_column(String(64), nullable=False, default="us-east-1")
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    sla_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=45)
    reputation_score: Mapped[float] = mapped_column(Float, nullable=False, default=94.0)
    sustainability_score: Mapped[float] = mapped_column(Float, nullable=False, default=88.0)
    availability: Mapped[str] = mapped_column(String(32), nullable=False, default="high")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    quotes: Mapped[list["NegotiationQuote"]] = relationship("NegotiationQuote", back_populates="provider")


class AutomationWorkflow(Base):
    __tablename__ = "automation_workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending_approval")
    selected_provider: Mapped[str | None] = mapped_column(String(128), nullable=True)
    workflow_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    quotes: Mapped[list["NegotiationQuote"]] = relationship("NegotiationQuote", back_populates="workflow", cascade="all, delete-orphan")
    steps: Mapped[list["WorkflowStep"]] = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")


class NegotiationQuote(Base):
    __tablename__ = "negotiation_quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(ForeignKey("automation_workflows.id", ondelete="CASCADE"), nullable=False)
    provider_id: Mapped[str | None] = mapped_column(ForeignKey("provider_profiles.id", ondelete="SET NULL"), nullable=True)
    provider_name: Mapped[str] = mapped_column(String(128), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sla_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=45)
    reputation_score: Mapped[float] = mapped_column(Float, nullable=False, default=90.0)
    sustainability_score: Mapped[float] = mapped_column(Float, nullable=False, default=80.0)
    decision_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    counter_offer: Mapped[str] = mapped_column(Text, nullable=False, default="")
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="quoted")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    workflow: Mapped["AutomationWorkflow"] = relationship("AutomationWorkflow", back_populates="quotes")
    provider: Mapped["ProviderProfile | None"] = relationship("ProviderProfile", back_populates="quotes")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(ForeignKey("automation_workflows.id", ondelete="CASCADE"), nullable=False)
    step_name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="queued")
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    workflow: Mapped["AutomationWorkflow"] = relationship("AutomationWorkflow", back_populates="steps")
