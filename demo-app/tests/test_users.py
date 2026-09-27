def test_register_and_me(client):
    resp = client.post("/users", json={"username": "carol"})
    assert resp.status_code == 201
    token = resp.get_json()["api_token"]
    me = client.get("/users/me", headers={"X-API-Token": token}).get_json()
    assert me["username"] == "carol"
    assert me["is_admin"] is False
    assert "api_token" not in me


def test_duplicate_username(client):
    client.post("/users", json={"username": "dave"})
    assert client.post("/users", json={"username": "dave"}).status_code == 409


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}
