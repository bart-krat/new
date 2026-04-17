"""Tests for Phase 2 state manager functions."""
import os
import json
import pytest
from app.state import manager
from app.models import Task, Constraints, TimeBlock


# Use test-specific data file
TEST_DATA_FILE = os.path.join(os.path.dirname(__file__), "test_manager_phase2_data.json")


@pytest.fixture(autouse=True)
def setup_test_file(monkeypatch):
    """Use a test-specific data file."""
    monkeypatch.setattr(manager, "DATA_FILE", TEST_DATA_FILE)
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)
    yield
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)


class TestGetTaskById:
    """Tests for get_task_by_id function."""

    def test_get_existing_task(self):
        """Returns task when ID exists."""
        tasks = manager.add_tasks(["Test task"])
        task_id = tasks[0].id

        result = manager.get_task_by_id(task_id)

        assert result is not None
        assert result.id == task_id
        assert result.text == "Test task"

    def test_get_nonexistent_task(self):
        """Returns None when ID doesn't exist."""
        result = manager.get_task_by_id("nonexistent-id")
        assert result is None

    def test_get_from_multiple_tasks(self):
        """Returns correct task when multiple exist."""
        manager.add_tasks(["First", "Second", "Third"])
        tasks = manager.get_tasks()
        target_id = tasks[1].id

        result = manager.get_task_by_id(target_id)

        assert result is not None
        assert result.text == "Second"


class TestUpdateTask:
    """Tests for update_task function."""

    def test_update_category(self):
        """Updates task category."""
        tasks = manager.add_tasks(["Test task"])
        task_id = tasks[0].id

        result = manager.update_task(task_id, category="work")

        assert result is not None
        assert result.category == "work"

    def test_update_duration(self):
        """Updates task duration."""
        tasks = manager.add_tasks(["Test task"])
        task_id = tasks[0].id

        result = manager.update_task(task_id, duration_minutes=45)

        assert result is not None
        assert result.duration_minutes == 45

    def test_update_multiple_fields(self):
        """Updates multiple fields at once."""
        tasks = manager.add_tasks(["Test task"])
        task_id = tasks[0].id

        result = manager.update_task(
            task_id, category="health", duration_minutes=60, confirmed=True
        )

        assert result is not None
        assert result.category == "health"
        assert result.duration_minutes == 60
        assert result.confirmed is True

    def test_update_preserves_other_fields(self):
        """Updating one field preserves others."""
        tasks = manager.add_tasks(["Test task"])
        task_id = tasks[0].id

        # First update
        manager.update_task(task_id, category="work")
        # Second update
        result = manager.update_task(task_id, duration_minutes=30)

        assert result.category == "work"  # Preserved
        assert result.duration_minutes == 30

    def test_update_nonexistent_task(self):
        """Returns None when task doesn't exist."""
        result = manager.update_task("nonexistent-id", category="work")
        assert result is None

    def test_update_persists_to_file(self):
        """Updates are persisted to file."""
        tasks = manager.add_tasks(["Test task"])
        task_id = tasks[0].id

        manager.update_task(task_id, category="personal")

        # Read directly from file
        with open(TEST_DATA_FILE, "r") as f:
            data = json.load(f)
        assert data["tasks"][0]["category"] == "personal"

    def test_update_with_none_value_ignored(self):
        """None values are ignored in updates."""
        tasks = manager.add_tasks(["Test task"])
        task_id = tasks[0].id
        manager.update_task(task_id, category="work")

        result = manager.update_task(task_id, category=None, duration_minutes=30)

        assert result.category == "work"  # Not changed to None
        assert result.duration_minutes == 30


class TestSaveConstraints:
    """Tests for save_constraints function."""

    def test_save_constraints(self):
        """Saves constraints to state."""
        constraints = Constraints(
            available_blocks=[TimeBlock(start="09:00", end="17:00")],
            category_weights={"work": 0.5, "personal": 0.3, "health": 0.2},
        )

        manager.save_constraints(constraints)

        # Verify saved
        with open(TEST_DATA_FILE, "r") as f:
            data = json.load(f)
        assert data["constraints"] is not None
        assert data["constraints"]["category_weights"]["work"] == 0.5

    def test_save_constraints_overwrites(self):
        """New constraints overwrite previous."""
        constraints1 = Constraints(
            available_blocks=[TimeBlock(start="09:00", end="17:00")],
            category_weights={"work": 0.5, "personal": 0.3, "health": 0.2},
        )
        constraints2 = Constraints(
            available_blocks=[TimeBlock(start="10:00", end="14:00")],
            category_weights={"work": 0.3, "personal": 0.5, "health": 0.2},
        )

        manager.save_constraints(constraints1)
        manager.save_constraints(constraints2)

        result = manager.get_constraints()
        assert result.available_blocks[0].start == "10:00"
        assert result.category_weights["work"] == 0.3


class TestGetConstraints:
    """Tests for get_constraints function."""

    def test_get_constraints_when_saved(self):
        """Returns saved constraints."""
        constraints = Constraints(
            available_blocks=[TimeBlock(start="08:00", end="12:00")],
            category_weights={"work": 0.4, "personal": 0.4, "health": 0.2},
        )
        manager.save_constraints(constraints)

        result = manager.get_constraints()

        assert result is not None
        assert len(result.available_blocks) == 1
        assert result.available_blocks[0].start == "08:00"
        assert result.category_weights["work"] == 0.4

    def test_get_constraints_when_none(self):
        """Returns None when no constraints saved."""
        result = manager.get_constraints()
        assert result is None

    def test_get_constraints_multiple_blocks(self):
        """Returns constraints with multiple blocks."""
        constraints = Constraints(
            available_blocks=[
                TimeBlock(start="09:00", end="12:00"),
                TimeBlock(start="13:00", end="17:00"),
            ],
            category_weights={"work": 0.5, "personal": 0.3, "health": 0.2},
        )
        manager.save_constraints(constraints)

        result = manager.get_constraints()

        assert len(result.available_blocks) == 2


class TestLoadDataStructure:
    """Tests for default data structure."""

    def test_default_includes_constraints(self):
        """Default data structure includes constraints field."""
        data = manager._load_data()
        assert "constraints" in data
        assert data["constraints"] is None
