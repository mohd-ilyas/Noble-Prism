"""
Risk Engine — multi-factor fraud and anomaly scoring.

Returns a float 0.0–1.0.  Higher = more suspicious.

Factors weighted:
  - Amount vs. agent historical baseline              (30%)
  - Unknown / unregistered agent identity             (25%)
  - Transaction velocity in rolling window            (20%)
  - Category / purpose entropy                        (15%)
  - Cross-border / currency mismatch signals          (10%)
"""
from __future__ import annotations

import math


def compute_risk_score(
    *,
    amount: float,
    agent_avg_tx: float,          # agent's average transaction amount
    is_known_agent: bool,
    velocity_in_window: int,      # how many tx agent made in last N seconds
    velocity_limit: int,          # policy velocity limit
    category: str,
    purpose: str,
    currency: str,
    agent_reputation: float,      # 0–100
    is_cross_border: bool = False,
) -> float:
    """Compute normalised risk score 0.0–1.0."""

    score = 0.0

    # 1. Unknown agent — major risk signal
    if not is_known_agent:
        score += 0.35

    # 2. Amount anomaly: how many σ above agent baseline?
    if agent_avg_tx > 0:
        ratio = amount / agent_avg_tx
        # log ratio gives diminishing returns on huge outliers
        amount_risk = min(0.30, 0.30 * math.log1p(max(0, ratio - 1)) / math.log1p(50))
    else:
        # First-ever transaction — slightly elevated
        amount_risk = 0.05 if amount < 100 else 0.12
    score += amount_risk

    # 3. Velocity
    if velocity_limit > 0:
        v_ratio = min(1.0, velocity_in_window / velocity_limit)
        score += 0.20 * v_ratio

    # 4. Reputation inversion — low reputation = higher risk
    rep_factor = max(0.0, (100 - agent_reputation) / 100)
    score += 0.10 * rep_factor

    # 5. Suspicious keywords in purpose
    text = (purpose + " " + category).lower()
    suspicious = ["unclassified", "unknown", "test", "mining", "gambling"]
    if any(k in text for k in suspicious):
        score += 0.15

    # 6. Cross-border flag
    if is_cross_border:
        score += 0.05

    # Clamp to [0, 1]
    return round(min(1.0, max(0.0, score)), 4)
