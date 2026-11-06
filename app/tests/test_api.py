"""API tests. Run with:  pytest -v

Each test gets a fresh in-memory SQLite database, so tests never touch
the real PostgreSQL data and don't depend on each other.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # one shared in-memory DB for the whole test
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_list(client):
    r = client.post("/tasks", json={"title": "Learn GitHub Actions"})
    assert r.status_code == 201
    task = r.json()
    assert task["title"] == "Learn GitHub Actions"
    assert task["done"] is False

    r = client.get("/tasks")
    assert [t["id"] for t in r.json()] == [task["id"]]


def test_update_task(client):
    task_id = client.post("/tasks", json={"title": "Write tests"}).json()["id"]
    r = client.patch(f"/tasks/{task_id}", json={"done": True})
    assert r.status_code == 200
    assert r.json()["done"] is True
    assert r.json()["title"] == "Write tests"  # unchanged


def test_delete_task(client):
    task_id = client.post("/tasks", json={"title": "Temp"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


@pytest.mark.parametrize("bad", [{"title": ""}, {}, {"title": "x" * 201}])
def test_invalid_input_rejected(client, bad):
    assert client.post("/tasks", json=bad).status_code == 422
