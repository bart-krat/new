"""Tests for Pydantic models."""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models import (
    Task,
    TasksInput,
    TasksResponse,
    TimeBlock,
    Constraints,
    ScheduledTask,
    Schedule,
    HealthResponse,
)


class TestTask:
    def test_task_minimal(self):
        """Task can be created with just id and text."""
        task = Task(id="123", text="Test task")
        assert task.id == "123"
        assert task.text == "Test task"
        assert task.category is None
        assert task.duration_minutes is None
        assert task.deadline is None
        assert task.confirmed is False

    def test_task_full(self):
        """Task can be created with all fields."""
        deadline = datetime(2024, 12, 31, 17, 0)
        task = Task(
            id="456",
            text="Complete report",
            category="work",
            duration_minutes=60,
            deadline=deadline,
            confirmed=True,
        )
        assert task.category == "work"
        assert task.duration_minutes == 60
        assert task.deadline == deadline
        assert task.confirmed is True

    def test_task_requires_id(self):
        """Task requires id field."""
        with pytest.raises(ValidationError):
            Task(text="No ID")

    def test_task_requires_text(self):
        """Task requires text field."""
        with pytest.raises(ValidationError):
            Task(id="123")


class TestTasksInput:
    def test_tasks_input_valid(self):
        """TasksInput accepts list of strings."""
        input = TasksInput(tasks=["Task 1", "Task 2"])
        assert input.tasks == ["Task 1", "Task 2"]

    def test_tasks_input_empty(self):
        """TasksInput accepts empty list."""
        input = TasksInput(tasks=[])
        assert input.tasks == []

    def test_tasks_input_requires_tasks(self):
        """TasksInput requires tasks field."""
        with pytest.raises(ValidationError):
            TasksInput()


class TestTasksResponse:
    def test_tasks_response_valid(self):
        """TasksResponse contains list of Task objects."""
        task = Task(id="1", text="Test")
        response = TasksResponse(tasks=[task])
        assert len(response.tasks) == 1
        assert response.tasks[0].id == "1"

    def test_tasks_response_empty(self):
        """TasksResponse accepts empty list."""
        response = TasksResponse(tasks=[])
        assert response.tasks == []


class TestTimeBlock:
    def test_time_block_valid(self):
        """TimeBlock stores start and end times."""
        block = TimeBlock(start="09:00", end="12:00")
        assert block.start == "09:00"
        assert block.end == "12:00"


class TestConstraints:
    def test_constraints_valid(self):
        """Constraints stores blocks and weights."""
        constraints = Constraints(
            available_blocks=[TimeBlock(start="09:00", end="17:00")],
            category_weights={"work": 0.5, "personal": 0.3, "health": 0.2},
        )
        assert len(constraints.available_blocks) == 1
        assert constraints.category_weights["work"] == 0.5

    def test_constraints_multiple_blocks(self):
        """Constraints supports multiple time blocks."""
        constraints = Constraints(
            available_blocks=[
                TimeBlock(start="09:00", end="12:00"),
                TimeBlock(start="13:00", end="17:00"),
            ],
            category_weights={"work": 1.0},
        )
        assert len(constraints.available_blocks) == 2


class TestScheduledTask:
    def test_scheduled_task_valid(self):
        """ScheduledTask has required scheduling fields."""
        start = datetime(2024, 1, 15, 9, 0)
        end = datetime(2024, 1, 15, 10, 0)
        scheduled = ScheduledTask(
            task_id="123", start_time=start, end_time=end, category="work"
        )
        assert scheduled.task_id == "123"
        assert scheduled.start_time == start
        assert scheduled.end_time == end
        assert scheduled.category == "work"


class TestSchedule:
    def test_schedule_valid(self):
        """Schedule contains metadata and scheduled tasks."""
        now = datetime.now()
        scheduled_task = ScheduledTask(
            task_id="1",
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 10, 0),
            category="work",
        )
        schedule = Schedule(id="sched-1", created_at=now, tasks=[scheduled_task])
        assert schedule.id == "sched-1"
        assert schedule.created_at == now
        assert len(schedule.tasks) == 1

    def test_schedule_empty_tasks(self):
        """Schedule can have empty task list."""
        schedule = Schedule(id="empty", created_at=datetime.now(), tasks=[])
        assert schedule.tasks == []


class TestHealthResponse:
    def test_health_response_valid(self):
        """HealthResponse stores status."""
        response = HealthResponse(status="ok")
        assert response.status == "ok"
