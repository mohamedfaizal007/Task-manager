import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# ─── Test DB (in-memory SQLite) ───────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def register_and_login(username="testuser", password="testpass123", email="test@example.com"):
    client.post("/auth/register", json={"username": username, "email": email, "password": password})
    res = client.post("/auth/login", json={"username": username, "password": password})
    return res.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ─── Auth Tests ───────────────────────────────────────────────────────────────

def test_register_success():
    res = client.post(
        "/auth/register",
        json={"username": "newuser", "email": "new@example.com", "password": "password123"},
    )
    assert res.status_code == 201
    assert res.json()["username"] == "newuser"


def test_register_duplicate_username():
    client.post("/auth/register", json={"username": "dupuser", "email": "dup@example.com", "password": "pass123"})
    res = client.post("/auth/register", json={"username": "dupuser", "email": "dup2@example.com", "password": "pass123"})
    assert res.status_code == 400


def test_login_success():
    client.post("/auth/register", json={"username": "loginuser", "email": "login@example.com", "password": "pass123"})
    res = client.post("/auth/login", json={"username": "loginuser", "password": "pass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password():
    client.post("/auth/register", json={"username": "wrongpass", "email": "wp@example.com", "password": "correct"})
    res = client.post("/auth/login", json={"username": "wrongpass", "password": "wrong"})
    assert res.status_code == 401


# ─── Task Tests ───────────────────────────────────────────────────────────────

def test_create_task():
    token = register_and_login("taskuser1", "pass1234", "t1@example.com")
    res = client.post("/tasks/", json={"title": "My Task", "description": "desc"}, headers=auth_headers(token))
    assert res.status_code == 201
    assert res.json()["title"] == "My Task"
    assert res.json()["completed"] is False


def test_get_tasks():
    token = register_and_login("taskuser2", "pass1234", "t2@example.com")
    client.post("/tasks/", json={"title": "Task A"}, headers=auth_headers(token))
    client.post("/tasks/", json={"title": "Task B"}, headers=auth_headers(token))
    res = client.get("/tasks/", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["total"] >= 2


def test_get_task_by_id():
    token = register_and_login("taskuser3", "pass1234", "t3@example.com")
    created = client.post("/tasks/", json={"title": "Single Task"}, headers=auth_headers(token)).json()
    res = client.get(f"/tasks/{created['id']}", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["title"] == "Single Task"


def test_mark_task_completed():
    token = register_and_login("taskuser4", "pass1234", "t4@example.com")
    task = client.post("/tasks/", json={"title": "Complete Me"}, headers=auth_headers(token)).json()
    res = client.put(f"/tasks/{task['id']}", json={"completed": True}, headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["completed"] is True


def test_delete_task():
    token = register_and_login("taskuser5", "pass1234", "t5@example.com")
    task = client.post("/tasks/", json={"title": "Delete Me"}, headers=auth_headers(token)).json()
    res = client.delete(f"/tasks/{task['id']}", headers=auth_headers(token))
    assert res.status_code == 204


def test_cannot_access_other_users_task():
    token1 = register_and_login("user_a", "pass1234", "a@example.com")
    token2 = register_and_login("user_b", "pass1234", "b@example.com")
    task = client.post("/tasks/", json={"title": "Private"}, headers=auth_headers(token1)).json()
    res = client.get(f"/tasks/{task['id']}", headers=auth_headers(token2))
    assert res.status_code == 404


def test_filter_completed_tasks():
    token = register_and_login("filteruser", "pass1234", "filter@example.com")
    t1 = client.post("/tasks/", json={"title": "Done"}, headers=auth_headers(token)).json()
    client.post("/tasks/", json={"title": "Pending"}, headers=auth_headers(token))
    client.put(f"/tasks/{t1['id']}", json={"completed": True}, headers=auth_headers(token))

    res = client.get("/tasks/?completed=true", headers=auth_headers(token))
    assert res.status_code == 200
    assert all(t["completed"] for t in res.json()["tasks"])


def test_unauthenticated_access():
    res = client.get("/tasks/")
    assert res.status_code == 403
