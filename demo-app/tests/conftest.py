import pytest

from app import create_app, db


@pytest.fixture()
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite3")})
    with app.app_context():
        db.init_db()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    resp = client.post("/users", json={"username": "alice"})
    return {"X-API-Token": resp.get_json()["api_token"]}
