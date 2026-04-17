from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FixedTimeConstraint(BaseModel):
    """
    Fixed time constraint for a task.
    Times are expressed as minutes from start of day (0 = midnight).
    Example: start_minutes=540 (9:00 AM), end_minutes=600 (10:00 AM)
    Only the permutation optimizer respects these constraints.
    """
    task_id: str
    start_minutes: int  # Minutes from start of day (0-1439)
    end_minutes: int    # Minutes from start of day (0-1439)


class Task(BaseModel):
    id: str
    text: str
    category: Optional[str] = None
    duration_minutes: int = 30  # Default 30 minutes
    deadline: Optional[datetime] = None
    confirmed: bool = False
    fixed_time_constraint: Optional[FixedTimeConstraint] = None


class TasksInput(BaseModel):
    tasks: list[str]


class TasksResponse(BaseModel):
    tasks: list[Task]


class CategorizeInput(BaseModel):
    task_ids: list[str]


class TimeBlock(BaseModel):
    start: str
    end: str


class Constraints(BaseModel):
    available_blocks: list[TimeBlock]
    category_weights: dict[str, float]


class ConstraintsSaveResponse(BaseModel):
    saved: bool


class ScheduledTask(BaseModel):
    task_id: str
    start_time: datetime
    end_time: datetime
    category: str


class Schedule(BaseModel):
    id: str
    created_at: datetime
    tasks: list[ScheduledTask]


class HealthResponse(BaseModel):
    status: str


class OptimizeInput(BaseModel):
    task_ids: list[str]
    constraints: Optional[Constraints] = None


class OptimizeResponse(BaseModel):
    schedule: Schedule
    algorithm_used: str


class ScheduleResponse(BaseModel):
    schedule: Optional[Schedule] = None


class FixedTimeConstraintsInput(BaseModel):
    """Input for saving fixed time constraints."""
    constraints: list[FixedTimeConstraint]


class FixedTimeConstraintsResponse(BaseModel):
    """Response after saving fixed time constraints."""
    saved: bool
    count: int
