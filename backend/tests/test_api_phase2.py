"""Tests for Phase 2 API endpoints (categorize, constraints)."""
import pytest
from unittest.mock import patch, MagicMock


class TestCategorizeEndpoint:
    """Tests for POST /api/categorize endpoint."""

    def test_categorize_tasks_success(self, client):
        """POST /api/categorize categorizes specified tasks."""
        # First create tasks
        client.post("/api/tasks", json={"tasks": ["Go to gym", "Send email"]})
        tasks_response = client.get("/api/tasks")
        task_ids = [t["id"] for t in tasks_response.json()["tasks"]]

        # Mock the categorizer to avoid OpenAI call
        with patch("app.orchestrator.categorize_tasks") as mock_cat:
            from app.models import Task
            mock_cat.return_value = [
                Task(id=task_ids[0], text="Go to gym", category="health", duration_minutes=45),
                Task(id=task_ids[1], text="Send email", category="work", duration_minutes=30),
            ]

            response = client.post("/api/categorize", json={"task_ids": task_ids})

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert len(data["tasks"]) == 2

    def test_categorize_empty_ids(self, client):
        """POST /api/categorize with empty IDs returns empty list."""
        response = client.post("/api/categorize", json={"task_ids": []})
        assert response.status_code == 200
        assert response.json() == {"tasks": []}

    def test_categorize_invalid_payload(self, client):
        """POST /api/categorize with invalid payload returns 422."""
        response = client.post("/api/categorize", json={"invalid": "data"})
        assert response.status_code == 422

    def test_categorize_nonexistent_ids(self, client):
        """POST /api/categorize with nonexistent IDs returns empty."""
        response = client.post("/api/categorize", json={"task_ids": ["fake-id-123"]})
        assert response.status_code == 200
        assert response.json() == {"tasks": []}


class TestConstraintsEndpoints:
    """Tests for constraints endpoints."""

    def test_save_constraints_success(self, client):
        """POST /api/constraints saves constraints."""
        constraints = {
            "available_blocks": [{"start": "09:00", "end": "12:00"}],
            "category_weights": {"work": 0.5, "personal": 0.3, "health": 0.2},
        }

        response = client.post("/api/constraints", json=constraints)

        assert response.status_code == 200
        assert response.json() == {"saved": True}

    def test_save_constraints_multiple_blocks(self, client):
        """POST /api/constraints accepts multiple time blocks."""
        constraints = {
            "available_blocks": [
                {"start": "09:00", "end": "12:00"},
                {"start": "13:00", "end": "17:00"},
            ],
            "category_weights": {"work": 0.4, "personal": 0.4, "health": 0.2},
        }

        response = client.post("/api/constraints", json=constraints)

        assert response.status_code == 200
        assert response.json() == {"saved": True}

    def test_save_constraints_invalid_payload(self, client):
        """POST /api/constraints with invalid payload returns 422."""
        response = client.post("/api/constraints", json={"invalid": "data"})
        assert response.status_code == 422

    def test_get_constraints_default(self, client):
        """GET /api/constraints returns defaults when none saved."""
        response = client.get("/api/constraints")
        assert response.status_code == 200
        data = response.json()
        assert "available_blocks" in data
        assert "category_weights" in data

    def test_get_constraints_after_save(self, client):
        """GET /api/constraints returns saved constraints."""
        constraints = {
            "available_blocks": [{"start": "10:00", "end": "14:00"}],
            "category_weights": {"work": 0.6, "personal": 0.2, "health": 0.2},
        }
        client.post("/api/constraints", json=constraints)

        response = client.get("/api/constraints")

        assert response.status_code == 200
        data = response.json()
        assert data["available_blocks"] == [{"start": "10:00", "end": "14:00"}]
        assert data["category_weights"]["work"] == 0.6

    def test_constraints_overwrite_previous(self, client):
        """POST /api/constraints overwrites previous constraints."""
        # Save first constraints
        client.post(
            "/api/constraints",
            json={
                "available_blocks": [{"start": "09:00", "end": "17:00"}],
                "category_weights": {"work": 0.5, "personal": 0.3, "health": 0.2},
            },
        )

        # Save new constraints
        new_constraints = {
            "available_blocks": [{"start": "08:00", "end": "12:00"}],
            "category_weights": {"work": 0.3, "personal": 0.5, "health": 0.2},
        }
        client.post("/api/constraints", json=new_constraints)

        # Verify new constraints are returned
        response = client.get("/api/constraints")
        data = response.json()
        assert data["available_blocks"] == [{"start": "08:00", "end": "12:00"}]
        assert data["category_weights"]["work"] == 0.3
