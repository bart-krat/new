from __future__ import annotations

import json
import os
import uuid
from typing import TYPE_CHECKING, Optional

from ..models import Constraints, FixedTimeConstraint, Task

if TYPE_CHECKING:
    from ..models import Schedule

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def _load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"tasks": [], "schedule": None, "constraints": None, "fixed_time_constraints": []}
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        # Ensure fixed_time_constraints key exists for backwards compatibility
        if "fixed_time_constraints" not in data:
            data["fixed_time_constraints"] = []
        return data


def _save_data(data: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def add_tasks(task_texts: list[str]) -> list[Task]:
    data = _load_data()
    new_tasks = []
    for text in task_texts:
        task = Task(id=str(uuid.uuid4()), text=text, duration_minutes=30)
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


def save_fixed_time_constraints(constraints: list[FixedTimeConstraint]) -> int:
    """Save fixed time constraints. Returns count of saved constraints."""
    data = _load_data()
    data["fixed_time_constraints"] = [c.model_dump() for c in constraints]

    # Also update tasks with their fixed time constraints
    task_constraint_map = {c.task_id: c for c in constraints}
    for task in data["tasks"]:
        task_id = task["id"]
        if task_id in task_constraint_map:
            task["fixed_time_constraint"] = task_constraint_map[task_id].model_dump()
        else:
            task["fixed_time_constraint"] = None

    _save_data(data)
    return len(constraints)


def get_fixed_time_constraints() -> list[FixedTimeConstraint]:
    """Get all saved fixed time constraints."""
    data = _load_data()
    return [FixedTimeConstraint(**c) for c in data.get("fixed_time_constraints", [])]


def set_task_fixed_constraint(
    task_id: str, start_minutes: int, end_minutes: int
) -> Optional[Task]:
    """Set a fixed time constraint for a specific task."""
    constraint = FixedTimeConstraint(
        task_id=task_id,
        start_minutes=start_minutes,
        end_minutes=end_minutes,
    )

    data = _load_data()

    # Update the task
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["fixed_time_constraint"] = constraint.model_dump()
            break
    else:
        return None

    # Update the constraints list
    ftc_list = data.get("fixed_time_constraints", [])
    # Remove existing constraint for this task if any
    ftc_list = [c for c in ftc_list if c["task_id"] != task_id]
    ftc_list.append(constraint.model_dump())
    data["fixed_time_constraints"] = ftc_list

    _save_data(data)
    return get_task_by_id(task_id)


def clear_task_fixed_constraint(task_id: str) -> Optional[Task]:
    """Remove fixed time constraint from a task."""
    data = _load_data()

    # Update the task
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["fixed_time_constraint"] = None
            break
    else:
        return None

    # Update the constraints list
    ftc_list = data.get("fixed_time_constraints", [])
    ftc_list = [c for c in ftc_list if c["task_id"] != task_id]
    data["fixed_time_constraints"] = ftc_list

    _save_data(data)
    return get_task_by_id(task_id)
