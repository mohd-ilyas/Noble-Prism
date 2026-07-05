"""
Noble Prism — Integration tests for the four demo scenarios.

Run with:  pytest tests/ -v
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models BEFORE importing Base so metadata is populated
import app.models  # noqa: F401 — registers all ORM models
from app.database.engine import Base, get_db
from app.main import app

# ── Test database (file-based SQLite for test isolation) ─────────────────────

TestSession = sessionmaker(autocommit=False, autoflush=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create schema and seed test data once for the entire test session."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragmas(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    TestSession.configure(bind=test_engine)

    # Create all tables on the TEST engine
    Base.metadata.create_all(bind=test_engine)

    db = TestSession()
    from app.database.seed import run as seed
    seed(db)
    db.close()

    yield

    # Cleanup (best-effort — file may be locked on Windows)
    import os
    Base.metadata.drop_all(bind=test_engine)
    try:
        if os.path.exists("test_noble_prism.db"):
            os.remove("test_noble_prism.db")
    except PermissionError:
        pass  # Windows file lock — cleanup happens on next run


@pytest.fixture(scope="session")
def client(setup_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Health check ──────────────────────────────────────────────────────────────

def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── Scenario 1 ─────────────────────────────────────────────────────────────────
# ResearchAgent purchases AWS GPU Compute $18 → approved, intent_score=96, risk_score low

def test_scenario_1_gpu_compute_approved(client: TestClient):
    r = client.post("/transactions/evaluate", json={
        "from": "openai-buyer-07",
        "to": "aws-c-broker",
        "amount": 18.0,
        "currency": "USD",
        "category": "gpu_compute",
        "purpose": "H100 GPU compute lease",
        "merchant": "AWS",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["decision"] == "approved", f"Expected approved, got: {data}"
    assert data["intent_score"] >= 90, f"Expected intent_score ≥ 90, got: {data['intent_score']}"
    assert data["risk_score"] < 0.30, f"Expected low risk, got: {data['risk_score']}"


# ── Scenario 2 ─────────────────────────────────────────────────────────────────
# ResearchAgent purchases Crypto Mining Hardware $5000 → blocked, intent_score=4

def test_scenario_2_crypto_mining_blocked(client: TestClient):
    r = client.post("/transactions/evaluate", json={
        "from": "openai-buyer-07",
        "to": "crypto-mining-market",
        "amount": 5000.0,
        "currency": "USD",
        "category": "mining",
        "purpose": "Crypto Mining Hardware",
        "merchant": "CryptoMiner",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["decision"] == "blocked", f"Expected blocked, got: {data}"
    assert data["intent_score"] == 4, f"Expected intent_score=4, got: {data['intent_score']}"


# ── Scenario 4 ─────────────────────────────────────────────────────────────────
# Amount > approval_threshold → human_approval_required

def test_scenario_4_human_approval_required(client: TestClient):
    # openai-buyer-07 has spend-ceiling-v3 policy with approval_threshold=$5,000
    # Sending $6,000 exceeds the threshold → human_approval_required
    r = client.post("/transactions/evaluate", json={
        "from": "openai-buyer-07",
        "to": "aws-c-broker",
        "amount": 6000.0,
        "currency": "USD",
        "category": "gpu_compute",
        "purpose": "Large GPU cluster reservation",
        "merchant": "AWS",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["decision"] in ("human_approval_required", "escalated"), f"Got: {data}"


# ── Agents endpoint ───────────────────────────────────────────────────────────

def test_list_agents(client: TestClient):
    r = client.get("/agents")
    assert r.status_code == 200
    agents = r.json()
    assert len(agents) >= 6
    names = [a["name"] for a in agents]
    assert "openai-buyer-07" in names
    assert "aws-c-broker" in names


def test_get_agent_by_name(client: TestClient):
    r = client.get("/agents/openai-buyer-07")
    assert r.status_code == 200
    a = r.json()
    assert a["name"] == "openai-buyer-07"
    assert a["reputation"] >= 90.0


def test_register_agent(client: TestClient):
    r = client.post("/agents/register", json={
        "name": "test-agent-pytest",
        "org": "TestOrg",
        "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjAN...\n-----END PUBLIC KEY-----",
        "wallet_address": "0xdeadbeefdeadbeefdeadbeefdeadbeef00000001",
    })
    assert r.status_code == 201
    a = r.json()
    assert a["name"] == "test-agent-pytest"
    assert a["reputation"] == 80.0


# ── Policies endpoint ─────────────────────────────────────────────────────────

def test_list_policies(client: TestClient):
    r = client.get("/policies")
    assert r.status_code == 200
    policies = r.json()
    assert len(policies) >= 6
    names = [p["name"] for p in policies]
    assert "spend-ceiling-v3" in names


# ── Ledger endpoint ───────────────────────────────────────────────────────────

def test_get_ledger(client: TestClient):
    r = client.get("/ledger")
    assert r.status_code == 200
    entries = r.json()
    # At least the seed approved transactions should be in the ledger
    assert len(entries) >= 1
    entry = entries[0]
    assert "hash" in entry
    assert "previous_hash" in entry
    assert "riskScore" in entry


# ── Insights endpoint ─────────────────────────────────────────────────────────

def test_get_insights(client: TestClient):
    r = client.get("/insights")
    assert r.status_code == 200
    data = r.json()
    assert "kpis" in data
    assert "volume_series" in data
    assert "insights" in data
    assert "events" in data
    assert len(data["volume_series"]) == 24


# ── Initiate real transaction ─────────────────────────────────────────────────

def test_initiate_transaction(client: TestClient):
    r = client.post("/transactions/initiate", json={
        "from": "mistral-relayer",
        "to": "stripe-relay-01",
        "amount": 5.0,
        "currency": "USDC",
        "category": "inference",
        "purpose": "Micro-inference test",
        "merchant": "Stripe",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["status"] in ("approved", "escalated", "blocked")
    assert "riskScore" in data
    assert "policyTrace" in data


# ── Kill switch ───────────────────────────────────────────────────────────────

def test_kill_switch_activate_and_release(client: TestClient):
    # Register a disposable agent
    client.post("/agents/register", json={
        "name": "disposable-agent-ks",
        "org": "TestOrg",
        "public_key": "key",
        "wallet_address": "0xdeadbeef" + "0" * 32,
    })

    r = client.post("/killswitch/activate", json={
        "agent_id": "disposable-agent-ks",
        "reason": "Test freeze",
        "risk_score": 0.99,
    })
    assert r.status_code == 200
    assert r.json()["status"] == "active"

    r = client.post("/killswitch/release", json={
        "agent_id": "disposable-agent-ks",
        "note": "Test release",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "released"


# ── Policy trace structure ────────────────────────────────────────────────────

def test_policy_trace_structure(client: TestClient):
    """Verify the policy trace matches the frontend PolicyTrace interface."""
    r = client.post("/transactions/evaluate", json={
        "from": "llama-compute-4",
        "to": "aws-c-broker",
        "amount": 50.0,
        "currency": "USD",
        "category": "gpu_compute",
        "purpose": "GPU inference workload",
    })
    assert r.status_code == 200
    data = r.json()
    assert "policy_trace" in data
    for step in data["policy_trace"]:
        assert "step" in step
        assert "detail" in step
        assert "passed" in step
        assert isinstance(step["passed"], bool)
