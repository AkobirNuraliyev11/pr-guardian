"""Tests for /reports/* endpoints."""
import secrets

import pytest


# ---------------------------------------------------------------------------
# Helper fixture: a second regular user
# ---------------------------------------------------------------------------

@pytest.fixture()
def other_headers(client):
    resp = client.post("/users", json={"username": "bob"})
    return {"X-API-Token": resp.get_json()["api_token"]}


# ---------------------------------------------------------------------------
# Helper fixture: an admin user (is_admin=1, inserted directly)
# ---------------------------------------------------------------------------

@pytest.fixture()
def admin_headers(app):
    token = secrets.token_urlsafe(32)
    with app.app_context():
        from app import db
        db.execute(
            "INSERT INTO users (username, api_token, is_admin) VALUES (?, ?, 1)",
            ("admin_user", token),
        )
    return {"X-API-Token": token}


# ---------------------------------------------------------------------------
# GET /reports/search
# ---------------------------------------------------------------------------

def test_search_requires_auth(client):
    assert client.get("/reports/search?q=anything").status_code == 401


def test_search_finds_matching_tasks(client, auth_headers):
    client.post("/tasks", json={"title": "Buy milk"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Fix bug"}, headers=auth_headers)
    resp = client.get("/reports/search?q=milk", headers=auth_headers)
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.get_json()]
    assert titles == ["Buy milk"]


def test_search_empty_query_returns_all(client, auth_headers):
    client.post("/tasks", json={"title": "Alpha"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Beta"}, headers=auth_headers)
    resp = client.get("/reports/search?q=", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_search_no_matches(client, auth_headers):
    client.post("/tasks", json={"title": "Hello"}, headers=auth_headers)
    resp = client.get("/reports/search?q=zzz", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_search_scoped_to_current_user(client, auth_headers, other_headers):
    client.post("/tasks", json={"title": "Alice task"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Bob task"}, headers=other_headers)
    resp = client.get("/reports/search?q=task", headers=auth_headers)
    titles = [t["title"] for t in resp.get_json()]
    assert titles == ["Alice task"]


def test_search_safe_against_sql_injection(client, auth_headers):
    client.post("/tasks", json={"title": "Normal"}, headers=auth_headers)
    resp = client.get("/reports/search?q=%27+UNION+SELECT+*+FROM+users--", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json() == []


# ---------------------------------------------------------------------------
# GET /reports/export/<task_id>
# ---------------------------------------------------------------------------

def test_export_requires_auth(client):
    assert client.get("/reports/export/1").status_code == 401


def test_export_returns_csv(client, auth_headers):
    task_id = client.post("/tasks", json={"title": "Report me"}, headers=auth_headers).get_json()["id"]
    resp = client.get(f"/reports/export/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.mimetype == "text/csv"
    assert b"Report me" in resp.data


def test_export_task_not_found(client, auth_headers):
    resp = client.get("/reports/export/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_export_idor_blocked(client, auth_headers, other_headers):
    """A user must not be able to export another user's task."""
    task_id = client.post("/tasks", json={"title": "Private"}, headers=auth_headers).get_json()["id"]
    resp = client.get(f"/reports/export/{task_id}", headers=other_headers)
    assert resp.status_code == 404


def test_export_includes_comments(client, app, auth_headers):
    task_id = client.post("/tasks", json={"title": "T"}, headers=auth_headers).get_json()["id"]
    # Insert a comment directly — the comments API is not part of this branch.
    with app.app_context():
        from app import db
        user_id = client.get("/users/me", headers=auth_headers).get_json()["id"]
        db.execute(
            "INSERT INTO comments (task_id, user_id, body) VALUES (?, ?, ?)",
            (task_id, user_id, "a note"),
        )
    resp = client.get(f"/reports/export/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert b"a note" in resp.data


# ---------------------------------------------------------------------------
# GET /reports/admin/activity
# ---------------------------------------------------------------------------

def test_admin_activity_requires_auth(client):
    assert client.get("/reports/admin/activity").status_code == 401


def test_admin_activity_forbidden_for_non_admin(client, auth_headers):
    resp = client.get("/reports/admin/activity", headers=auth_headers)
    assert resp.status_code == 403


def test_admin_activity_query_param_bypass_blocked(client):
    """?admin=1 must NOT grant access — it must still return 401."""
    resp = client.get("/reports/admin/activity?admin=1")
    assert resp.status_code == 401


def test_admin_activity_returns_report(client, auth_headers, admin_headers):
    client.post("/tasks", json={"title": "Alice task"}, headers=auth_headers)
    resp = client.get("/reports/admin/activity", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    titles = [r["task"] for r in data if r["task"] is not None]
    assert "Alice task" in titles


# ---------------------------------------------------------------------------
# GET /reports/tags
# ---------------------------------------------------------------------------

def test_tags_requires_auth(client):
    assert client.get("/reports/tags").status_code == 401


def test_tags_empty_for_new_user(client, auth_headers):
    resp = client.get("/reports/tags", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json() == {"tags": [], "count": 0}


def test_tags_returns_unique_tags(client, auth_headers):
    client.post("/tasks", json={"title": "A", "tags": ["api", "docs"]}, headers=auth_headers)
    client.post("/tasks", json={"title": "B", "tags": ["api", "web"]}, headers=auth_headers)
    resp = client.get("/reports/tags", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert set(body["tags"]) == {"api", "docs", "web"}
    assert body["count"] == 3


def test_tags_scoped_to_current_user(client, auth_headers, other_headers):
    client.post("/tasks", json={"title": "A", "tags": ["alicetag"]}, headers=auth_headers)
    client.post("/tasks", json={"title": "B", "tags": ["bobtag"]}, headers=other_headers)
    resp = client.get("/reports/tags", headers=auth_headers)
    tags = resp.get_json()["tags"]
    assert "alicetag" in tags
    assert "bobtag" not in tags
