"""
Velocity Service — counts transactions for an agent within a rolling window.
Pure-SQL implementation; no Redis required.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.transaction import Transaction


def count_in_window(db: Session, agent_name: str) -> int:
    """
    Count how many transactions the named agent has initiated in the last
    VELOCITY_WINDOW_SECONDS.  Uses from_agent string for broad compatibility
    (works even before agent is fully registered).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.VELOCITY_WINDOW_SECONDS)
    count = (
        db.query(func.count(Transaction.id))
        .filter(
            Transaction.from_agent == agent_name,
            Transaction.created_at >= cutoff,
            Transaction.status != "pending",  # only committed decisions count
        )
        .scalar()
    ) or 0
    return int(count)


def check_kill_switch_threshold(db: Session, agent_name: str) -> bool:
    """
    Returns True if the agent has met or exceeded the velocity threshold and should
    trigger the kill switch (RULE 3).

    We check >= VELOCITY_MAX_TRANSACTIONS - 1 so that when the incoming request
    would be the Nth transaction (where N == threshold), we fire before committing it.
    This ensures exactly N purchases in the window triggers the kill switch.
    """
    threshold = settings.VELOCITY_MAX_TRANSACTIONS
    return count_in_window(db, agent_name) >= max(1, threshold - 1)
