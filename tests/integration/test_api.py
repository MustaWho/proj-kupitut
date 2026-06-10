"""API integration tests."""


def create_user(client, email: str = "owner@example.com", username: str = "owner") -> int:
    response = client.post(
        "/api/v1/users",
        json={"email": email, "username": username, "password": "secret123"},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def create_project(client, owner_id: int, name: str = "Backend") -> int:
    response = client.post(
        "/api/v1/projects",
        json={"owner_id": owner_id, "name": name, "status": "active"},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_health_aliases(client) -> None:
    assert client.get("/api/v1/health").status_code == 200
    assert client.get("/api/health").json()["status"] == "ok"


def test_user_api_crud_and_validation(client) -> None:
    user_id = create_user(client)

    duplicate = client.post(
        "/api/v1/users",
        json={"email": "owner@example.com", "username": "other", "password": "secret123"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "conflict"

    assert client.get(f"/api/v1/users/{user_id}").json()["username"] == "owner"
    assert len(client.get("/api/v1/users").json()) == 1

    patched = client.patch(f"/api/v1/users/{user_id}", json={"is_active": False})
    assert patched.status_code == 200
    assert patched.json()["is_active"] is False

    invalid = client.post(
        "/api/v1/users",
        json={"email": "bad", "username": "x", "password": "short"},
    )
    assert invalid.status_code == 422


def test_project_and_task_api_flow(client) -> None:
    owner_id = create_user(client)
    project_id = create_project(client, owner_id)

    task_response = client.post(
        "/api/v1/tasks",
        json={
            "project_id": project_id,
            "assignee_id": owner_id,
            "title": "Critical checkout error",
            "description": "Urgent blocker and error for payment flow.",
            "priority": 5,
            "tag_names": ["bug", "payments"],
        },
    )
    assert task_response.status_code == 201
    task = task_response.json()
    assert task["tags"][0]["name"] == "bug"

    listed = client.get("/api/v1/tasks", params={"project_id": project_id, "status": "todo"})
    assert len(listed.json()) == 1

    patched = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"status": "done", "tag_names": ["done"]},
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "done"

    analysis = client.post(f"/api/v1/tasks/{task['id']}/summary")
    assert analysis.status_code == 200
    assert analysis.json()["priority_score"] == 5

    assert client.delete(f"/api/v1/tasks/{task['id']}").status_code == 204
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 404


def test_project_errors_and_delete(client) -> None:
    missing_owner = client.post("/api/v1/projects", json={"owner_id": 999, "name": "Bad"})
    assert missing_owner.status_code == 404

    owner_id = create_user(client)
    project_id = create_project(client, owner_id)
    duplicate = client.post("/api/v1/projects", json={"owner_id": owner_id, "name": "Backend"})
    assert duplicate.status_code == 409

    assert (
        client.patch(f"/api/v1/projects/{project_id}", json={"status": "archived"}).status_code
        == 200
    )
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 204
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404


def test_task_validation_and_missing_refs(client) -> None:
    response = client.post("/api/v1/tasks", json={"project_id": 404, "title": "Missing"})
    assert response.status_code == 404

    owner_id = create_user(client)
    project_id = create_project(client, owner_id)
    invalid = client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Ok title", "tag_names": ["!"]},
    )
    assert invalid.status_code == 422


def test_analysis_endpoint_and_root(client) -> None:
    response = client.post(
        "/api/v1/analysis/analyze",
        json={"text": "Great result with fast progress and stable release."},
    )
    assert response.status_code == 200
    assert response.json()["sentiment"] == "positive"
    assert client.get("/").json()["docs"] == "/docs"
