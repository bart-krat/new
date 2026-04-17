from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    CategorizeInput,
    Constraints,
    ConstraintsSaveResponse,
    FixedTimeConstraint,
    FixedTimeConstraintsInput,
    FixedTimeConstraintsResponse,
    HealthResponse,
    OptimizeInput,
    OptimizeResponse,
    ScheduleResponse,
    TasksInput,
    TasksResponse,
)
from .orchestrator import orchestrator
from .state import manager

app = FastAPI(title="AI Daily Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok")


@app.post("/api/tasks", response_model=TasksResponse)
def create_tasks(input: TasksInput):
    tasks = manager.add_tasks(input.tasks)
    return TasksResponse(tasks=tasks)


@app.get("/api/tasks", response_model=TasksResponse)
def get_tasks():
    tasks = manager.get_tasks()
    return TasksResponse(tasks=tasks)


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    deleted = manager.delete_task(task_id)
    return {"deleted": deleted}


@app.delete("/api/tasks")
def clear_all_tasks():
    manager.clear_tasks()
    return {"cleared": True}


@app.post("/api/categorize", response_model=TasksResponse)
def categorize_tasks(input: CategorizeInput):
    tasks = orchestrator.categorize(input.task_ids)
    return TasksResponse(tasks=tasks)


@app.post("/api/constraints", response_model=ConstraintsSaveResponse)
def save_constraints(constraints: Constraints):
    orchestrator.save_constraints(constraints)
    return ConstraintsSaveResponse(saved=True)


@app.get("/api/constraints")
def get_constraints():
    constraints = orchestrator.get_constraints()
    if constraints:
        return constraints.model_dump()
    return {"available_blocks": [], "category_weights": {"work": 0.4, "personal": 0.3, "health": 0.3}}


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize_tasks(input: OptimizeInput):
    schedule, algorithm = orchestrator.optimize(input.task_ids, input.constraints)
    return OptimizeResponse(schedule=schedule, algorithm_used=algorithm)


@app.get("/api/schedule", response_model=ScheduleResponse)
def get_schedule():
    schedule = orchestrator.get_schedule()
    return ScheduleResponse(schedule=schedule)


@app.post("/api/fixed-time-constraints", response_model=FixedTimeConstraintsResponse)
def save_fixed_time_constraints(input: FixedTimeConstraintsInput):
    """Save fixed time constraints for tasks."""
    count = manager.save_fixed_time_constraints(input.constraints)
    return FixedTimeConstraintsResponse(saved=True, count=count)


@app.get("/api/fixed-time-constraints")
def get_fixed_time_constraints():
    """Get all fixed time constraints."""
    constraints = manager.get_fixed_time_constraints()
    return {"constraints": [c.model_dump() for c in constraints]}


@app.put("/api/tasks/{task_id}/fixed-time-constraint")
def set_task_fixed_constraint(task_id: str, constraint: FixedTimeConstraint):
    """Set a fixed time constraint for a specific task."""
    task = manager.set_task_fixed_constraint(
        task_id, constraint.start_minutes, constraint.end_minutes
    )
    if task:
        return task.model_dump()
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/api/tasks/{task_id}/fixed-time-constraint")
def clear_task_fixed_constraint(task_id: str):
    """Remove fixed time constraint from a task."""
    task = manager.clear_task_fixed_constraint(task_id)
    if task:
        return task.model_dump()
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/api/tasks/{task_id}/duration")
def update_task_duration(task_id: str, duration: dict):
    """Update the duration of a task."""
    task = manager.update_task(task_id, duration_minutes=duration.get("duration_minutes"))
    if task:
        return task.model_dump()
    raise HTTPException(status_code=404, detail="Task not found")
