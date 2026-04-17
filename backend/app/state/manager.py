from __future__ import annotations

import json
import os
import uuid
from typing import TYPE_CHECKING, Optional

from ..models import Constraints, Task

if TYPE_CHECKING:
    from ..models import Schedule

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def _load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"tasks": [], "schedule": None, "constraints": None}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save_data(data: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def add_tasks(task_texts: list[str]) -> list[Task]:
    data = _load_data()
    new_tasks = []
    for text in task_texts:
        task = Task(id=str(uuid.uuid4()), text=text)
        new_tasks.append(task)
        data["tasks"].append(task.model_dump())
    _save_data(data)
    return new_tasks


def get_tasks() -> list[Task]:
    data = _load_data()
    return [Task(**t) for t in data["tasks"]]


def get_task_by_id(task_id: str) -> Optional[Task]:
    tasks = get_tasks()
    for t in tasks:
        if t.id == task_id:
            return t
    return None


def update_task(task_id: str, **kwargs) -> Optional[Task]:
    """Update task fields by ID."""
    data = _load_data()
    for i, t in enumerate(data["tasks"]):
        if t["id"] == task_id:
            for key, value in kwargs.items():
                if value is not None:
                    t[key] = value
            data["tasks"][i] = t
            _save_data(data)
            return Task(**t)
    return None


def clear_tasks() -> None:
    data = _load_data()
    data["tasks"] = []
    data["schedule"] = None  # Also clear schedule when tasks are cleared
    _save_data(data)


def delete_task(task_id: str) -> bool:
    """Delete a task by ID. Returns True if deleted."""
    data = _load_data()
    original_len = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    if len(data["tasks"]) < original_len:
        _save_data(data)
        return True
    return False


def save_constraints(constraints: Constraints) -> None:
    data = _load_data()
    data["constraints"] = constraints.model_dump()
    _save_data(data)


def get_constraints() -> Optional[Constraints]:
    data = _load_data()
    c = data.get("constraints")
    if c:
        return Constraints(**c)
    return None


def save_schedule(schedule: Schedule) -> None:
    """Save schedule to state."""
    data = _load_data()
    data["schedule"] = schedule.model_dump()
    _save_data(data)


def get_schedule() -> Optional[Schedule]:
    """Get saved schedule."""
    from ..models import Schedule as ScheduleModel

    data = _load_data()
    s = data.get("schedule")
    if s:
        return ScheduleModel(**s)
    return None
