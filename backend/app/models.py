from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Task(BaseModel):
    id: str
    text: str
    category: Optional[str] = None
    duration_minutes: Optional[int] = None
    deadline: Optional[datetime] = None
    confirmed: bool = False


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
