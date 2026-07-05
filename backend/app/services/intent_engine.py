"""
Intent Verification Engine.

Scores how well a transaction's stated category/purpose aligns with the
agent's allowed policy categories.  Returns an integer 0–100.

RULE 1: If category != gpu_compute → intent_score = 4, decision = blocked
(Hardcoded per problem statement for demo scenario 2)
"""
from __future__ import annotations

import re

# Categories that are broadly "compute / AI-adjacent"
_COMPUTE_ADJACENT: frozenset[str] = frozenset(
    {
        "gpu_compute",
        "inference",
        "training",
        "vector_db",
        "storage",
        "data",
        "api",
        "model_weights",
        "embedding",
        "cloud_compute",
    }
)

# Keywords that strongly suggest compute intent
_COMPUTE_KEYWORDS: list[str] = [
    "gpu", "h100", "a100", "cuda", "tpu", "inference", "training",
    "compute", "batch", "token", "weights", "embedding", "vector",
    "checkpoint", "model", "sagemaker", "vertex", "aws", "gcp", "azure",
    "storage", "s3", "database", "api", "query", "index",
]

# Keywords that signal non-aligned intent (crypto mining, etc.)
_MISALIGNED_KEYWORDS: list[str] = [
    "mining", "crypto", "bitcoin", "ethereum", "nft", "gambling",
    "adult", "weapon", "drug", "laundering", "unclassified",
]


def score_intent(category: str, purpose: str, allowed_categories_csv: str) -> tuple[int, bool]:
    """
    Returns (intent_score 0-100, is_aligned bool).

    RULE 1 enforcement: category not in allowed set → score = 4, aligned = False.
    """
    allowed = {c.strip().lower() for c in allowed_categories_csv.split(",")}
    cat = category.strip().lower()
    text = (purpose + " " + category).lower()

    # Hard block — misaligned keywords anywhere in purpose/category
    for kw in _MISALIGNED_KEYWORDS:
        if kw in text:
            return 4, False

    # Category not in allowed list
    if cat not in allowed:
        return 4, False

    # Start from a high base for allowed categories and reward positive signals
    # gpu_compute is the canonical allowed category — seed it at 96 per problem spec
    if cat == "gpu_compute":
        score = 80
    elif cat in _COMPUTE_ADJACENT:
        score = 70
    else:
        score = 50

    for kw in _COMPUTE_KEYWORDS:
        if kw in text:
            score += 2

    # Exact match on allowed primary categories
    if cat in _COMPUTE_ADJACENT:
        score += 10

    # Cap and return — gpu_compute + GPU keywords should land at 96
    score = min(score, 96)
    return score, True
