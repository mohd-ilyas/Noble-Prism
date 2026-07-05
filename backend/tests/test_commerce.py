from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database.engine import Base, get_db
from app.main import app

TestSession = sessionmaker(autocommit=False, autoflush=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragmas(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    TestSession.configure(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestSession()
    from app.database.seed import run as seed

    seed(db)
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def client(setup_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_commerce_providers(client: TestClient):
    response = client.get("/commerce/providers")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 3
    assert payload[0]["provider_name"]


def test_create_workflow_and_approve(client: TestClient):
    response = client.post(
        "/commerce/workflows",
        json={
            "goal": "Find a sustainable GPU provider for a training burst",
            "amount": 125.0,
            "currency": "USD",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] in {"pending_approval", "queued", "running"}
    workflow_id = payload["id"]

    approve_response = client.post(f"/commerce/workflows/{workflow_id}/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "running"

    retry_response = client.post(f"/commerce/workflows/{workflow_id}/retry")
    assert retry_response.status_code == 200
    assert retry_response.json()["status"] == "queued"


def test_get_provider_and_quotes(client: TestClient):
    providers = client.get("/commerce/providers")
    assert providers.status_code == 200
    provider_id = providers.json()[0]["id"]

    provider_detail = client.get(f"/commerce/providers/{provider_id}")
    assert provider_detail.status_code == 200
    assert provider_detail.json()["id"] == provider_id

    workflow = client.post(
        "/commerce/workflows",
        json={"goal": "Compare backup GPU suppliers", "amount": 60.0, "currency": "USD"},
    )
    assert workflow.status_code == 201
    workflow_id = workflow.json()["id"]

    quotes = client.get(f"/commerce/workflows/{workflow_id}/quotes")
    assert quotes.status_code == 200
    assert isinstance(quotes.json(), list)
    assert len(quotes.json()) >= 1
