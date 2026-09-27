def test_requires_token(client):
    assert client.get("/tasks").status_code == 401


def test_create_and_list(client, auth_headers):
    resp = client.post(
        "/tasks", json={"title": "Write docs", "tags": ["Docs", "docs ", "api"]}, headers=auth_headers
    )
    assert resp.status_code == 201
    assert resp.get_json()["tags"] == "api,docs"
    tasks = client.get("/tasks", headers=auth_headers).get_json()
    assert [t["title"] for t in tasks] == ["Write docs"]


def test_empty_title_rejected(client, auth_headers):
    assert client.post("/tasks", json={"title": "  "}, headers=auth_headers).status_code == 400


def test_status_update_and_filter(client, auth_headers):
    task_id = client.post("/tasks", json={"title": "A"}, headers=auth_headers).get_json()["id"]
    done = client.patch(f"/tasks/{task_id}", json={"status": "done"}, headers=auth_headers)
    assert done.get_json()["status"] == "done"
    bad = client.patch(f"/tasks/{task_id}", json={"status": "bogus"}, headers=auth_headers)
    assert bad.status_code == 400
    assert len(client.get("/tasks?status=done", headers=auth_headers).get_json()) == 1


def test_users_cannot_see_each_others_tasks(client, auth_headers):
    task_id = client.post("/tasks", json={"title": "Private"}, headers=auth_headers).get_json()["id"]
    other = {"X-API-Token": client.post("/users", json={"username": "bob"}).get_json()["api_token"]}
    assert client.get(f"/tasks/{task_id}", headers=other).status_code == 404
    assert client.delete(f"/tasks/{task_id}", headers=other).status_code == 404


def test_delete(client, auth_headers):
    task_id = client.post("/tasks", json={"title": "Temp"}, headers=auth_headers).get_json()["id"]
    assert client.delete(f"/tasks/{task_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 404
