from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    CategorizeInput,
    Constraints,
    ConstraintsSaveResponse,
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
