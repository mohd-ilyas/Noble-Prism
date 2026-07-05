"""
Noble Prism — Agent-to-Agent Payment Protocol
FastAPI application entry point.
"""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.engine import Base, SessionLocal, engine
from app.database.seed import run as seed_db
from app.routes import (
    agents_router,
    commerce_router,
    insights_router,
    killswitch_router,
    ledger_router,
    policies_router,
    transactions_router,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("noble_prism")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed demo data on startup."""
    logger.info("Noble Prism backend starting…")

    # Import all models so Base knows about them before create_all
    import app.models  # noqa: F401 — registers ORM metadata

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Seed demo data (idempotent)
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()

    logger.info("Noble Prism ready — environment: %s", settings.ENVIRONMENT)
    yield
    logger.info("Noble Prism shutting down")


app = FastAPI(
    title="Noble Prism — Autonomous AI Commerce Operating System",
    description="""
## Noble Prism API

Production-grade backend for autonomous machine-to-machine payments.

### Key capabilities
- **Identity & Wallet Abstraction** — register and manage AI agents
- **Spending Policies** — per-agent daily limits, category allow-lists, velocity guards
- **Real-time Authorization** — sub-20ms policy evaluation pipeline
- **Fraud & Anomaly Detection** — multi-factor risk scoring engine
- **Tamper-evident Ledger** — SHA-256 hash-chained settlement records
- **Human Approval Escalation** — escalated transactions routed to on-call operators
- **Kill Switch** — instant agent freeze on velocity anomaly or manual trigger
- **Reputation System** — rolling reputation score updated on every decision

### Demo Scenarios
| Scenario | Input | Expected |
|----------|-------|----------|
| 1 | ResearchAgent + AWS GPU $18 | approved, intent_score=96 |
| 2 | ResearchAgent + Crypto Mining $5000 | blocked, intent_score=4 |
| 3 | 20 purchases in 2 minutes | kill switch activated |
| 4 | Amount > approval_threshold | human_approval_required |
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request timing middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    t0 = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        if "response" in locals():
            response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
            response.headers["X-Request-ID"] = request_id
        logger.info(
            "%s %s completed in %sms request_id=%s",
            request.method,
            request.url.path,
            elapsed_ms,
            request_id,
        )


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.exception("Unhandled exception request_id=%s", request_id)
    return JSONResponse(
        status_code=500,
        headers={"X-Request-ID": request_id},
        content={"detail": "Internal server error", "request_id": request_id},
    )


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(agents_router)
app.include_router(policies_router)
app.include_router(transactions_router)
app.include_router(ledger_router)
app.include_router(insights_router)
app.include_router(killswitch_router)
app.include_router(commerce_router)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"], summary="Health check")
def health():
    """Liveness probe — returns 200 when the service is up."""
    return {
        "status": "ok",
        "service": "noble-prism-backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System"], summary="API root")
def root():
    return {
        "name": "Noble Prism — Autonomous AI Commerce Operating System",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
    }
