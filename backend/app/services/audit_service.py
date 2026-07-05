"""
Audit Service — writes structured, immutable audit log entries.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


_EVENT_DOT_MAP: dict[str, str] = {
    "TRANSACTION_APPROVED": "success",
    "TRANSACTION_BLOCKED": "danger",
    "TRANSACTION_ESCALATED": "warning",
    "TRANSACTION_REJECTED": "danger",
    "KILL_SWITCH_ACTIVATED": "danger",
    "KILL_SWITCH_RELEASED": "success",
    "AGENT_REGISTERED": "primary",
    "AGENT_FROZEN": "danger",
    "POLICY_CREATED": "primary",
    "POLICY_UPDATED": "secondary",
    "LEDGER_COMMITTED": "success",
    "WORKFLOW_CREATED": "primary",
    "WORKFLOW_APPROVED": "success",
    "WORKFLOW_RETRIED": "warning",
}


def log(
    db: Session,
    *,
    event_type: str,
    description: str,
    transaction_id: str | None = None,
    agent_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    dot = _EVENT_DOT_MAP.get(event_type, "primary")
    entry = AuditLog(
        transaction_id=transaction_id,
        agent_id=agent_id,
        event_type=event_type,
        description=description,
        metadata_json=json.dumps(metadata or {}),
        dot=dot,
    )
    db.add(entry)
    return entry
