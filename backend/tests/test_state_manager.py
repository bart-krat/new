"""Tests for state manager module."""
import os
import json
import pytest
from app.state import manager
from app.models import Task


# Override the data file path for tests
TEST_DATA_FILE = os.path.join(os.path.dirname(__file__), "test_manager_data.json")


@pytest.fixture(autouse=True)
def setup_test_file(monkeypatch):
    """Use a test-specific data file."""
    monkeypatch.setattr(manager, "DATA_FILE", TEST_DATA_FILE)
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)
    yield
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)


def test_add_tasks_creates_tasks():
    """add_tasks creates Task objects from text."""
    tasks = manager.add_tasks(["Task 1", "Task 2"])
    assert len(tasks) == 2
    assert isinstance(tasks[0], Task)
    assert tasks[0].text == "Task 1"
    assert tasks[1].text == "Task 2"


def test_add_tasks_generates_ids():
    """add_tasks generates unique UUIDs for each task."""
    tasks = manager.add_tasks(["Task A", "Task B"])
    assert tasks[0].id is not None
    assert tasks[1].id is not None
    assert tasks[0].id != tasks[1].id
    # Check it's a valid UUID format
    assert len(tasks[0].id) == 36


def test_add_tasks_sets_defaults():
    """add_tasks sets default values for new tasks."""
    tasks = manager.add_tasks(["Test"])
    task = tasks[0]
    assert task.category is None
    assert task.duration_minutes is None
    assert task.deadline is None
    assert task.confirmed is False


def test_get_tasks_empty():
    """get_tasks returns empty list when no tasks exist."""
    tasks = manager.get_tasks()
    assert tasks == []


def test_get_tasks_returns_added_tasks():
    """get_tasks returns all previously added tasks."""
    manager.add_tasks(["First", "Second"])
    tasks = manager.get_tasks()
    assert len(tasks) == 2
    assert tasks[0].text == "First"
    assert tasks[1].text == "Second"


def test_tasks_persist_to_file():
    """Tasks are saved to JSON file."""
    manager.add_tasks(["Persistent task"])
    assert os.path.exists(TEST_DATA_FILE)
    with open(TEST_DATA_FILE, "r") as f:
        data = json.load(f)
    assert "tasks" in data
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["text"] == "Persistent task"


def test_clear_tasks():
    """clear_tasks removes all tasks."""
    manager.add_tasks(["To be deleted"])
    manager.clear_tasks()
    tasks = manager.get_tasks()
    assert tasks == []


def test_clear_tasks_preserves_file_structure():
    """clear_tasks keeps file structure intact."""
    manager.add_tasks(["Task"])
    manager.clear_tasks()
    with open(TEST_DATA_FILE, "r") as f:
        data = json.load(f)
    assert "tasks" in data
    assert data["tasks"] == []


def test_add_tasks_accumulates():
    """Multiple add_tasks calls accumulate tasks."""
    manager.add_tasks(["First batch"])
    manager.add_tasks(["Second batch"])
    tasks = manager.get_tasks()
    assert len(tasks) == 2


def test_add_empty_list():
    """add_tasks with empty list returns empty and doesn't error."""
    tasks = manager.add_tasks([])
    assert tasks == []


def test_load_data_creates_default_structure():
    """Loading non-existent file returns default structure."""
    data = manager._load_data()
    assert data == {"tasks": [], "schedule": None, "constraints": None}
