"""Tests for API endpoints."""


def test_health_check(client):
    """GET /api/health returns ok status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_tasks(client):
    """POST /api/tasks creates new tasks."""
    response = client.post("/api/tasks", json={"tasks": ["Buy groceries", "Call mom"]})
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) == 2
    assert data["tasks"][0]["text"] == "Buy groceries"
    assert data["tasks"][1]["text"] == "Call mom"


def test_create_tasks_returns_task_structure(client):
    """Created tasks have correct structure."""
    response = client.post("/api/tasks", json={"tasks": ["Test task"]})
    task = response.json()["tasks"][0]
    assert "id" in task
    assert task["text"] == "Test task"
    assert task["category"] is None
    assert task["duration_minutes"] == 30  # Default 30 minutes
    assert task["deadline"] is None
    assert task["confirmed"] is False


def test_create_tasks_generates_unique_ids(client):
    """Each task gets a unique ID."""
    response = client.post("/api/tasks", json={"tasks": ["Task 1", "Task 2"]})
    tasks = response.json()["tasks"]
    assert tasks[0]["id"] != tasks[1]["id"]


def test_get_tasks_empty(client):
    """GET /api/tasks returns empty list when no tasks exist."""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": []}


def test_get_tasks_returns_created_tasks(client):
    """GET /api/tasks returns previously created tasks."""
    client.post("/api/tasks", json={"tasks": ["Task A", "Task B"]})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) == 2
    assert tasks[0]["text"] == "Task A"
    assert tasks[1]["text"] == "Task B"


def test_create_tasks_empty_list(client):
    """POST /api/tasks with empty list creates no tasks."""
    response = client.post("/api/tasks", json={"tasks": []})
    assert response.status_code == 200
    assert response.json() == {"tasks": []}


def test_tasks_persist_across_requests(client):
    """Tasks are persisted and accumulate across multiple POST requests."""
    client.post("/api/tasks", json={"tasks": ["First task"]})
    client.post("/api/tasks", json={"tasks": ["Second task"]})
    response = client.get("/api/tasks")
    tasks = response.json()["tasks"]
    assert len(tasks) == 2


def test_create_tasks_invalid_payload(client):
    """POST /api/tasks with invalid payload returns 422."""
    response = client.post("/api/tasks", json={"invalid": "data"})
    assert response.status_code == 422


def test_create_tasks_missing_body(client):
    """POST /api/tasks without body returns 422."""
    response = client.post("/api/tasks")
    assert response.status_code == 422
