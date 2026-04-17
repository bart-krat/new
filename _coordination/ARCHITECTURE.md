# Architecture

## What We're Building

An AI-powered daily planner that takes free-text task input, categorizes tasks using an LLM (personal/work/health), and generates an optimized daily schedule based on user-defined time constraints and category utility weights. The system uses multiple optimization algorithms (greedy, knapsack, permutation) with LLM fallback, selected based on constraint complexity.

**Key user need:** Morning planning workflow that turns a brain dump of tasks into a structured, optimized schedule.

## Tech Stack

**Frontend:** React (Vite + TypeScript)
**Backend:** FastAPI (Python 3.11+)
**LLM:** OpenAI API (key via .env)
**State:** JSON file persistence (prototype)
**Deployment:** Local development (Docker-ready structure for later)

**Rationale:** React + FastAPI is a proven pairing for AI-driven apps. Python backend allows easy integration with optimization libraries (scipy, ortools) and OpenAI SDK. JSON persistence keeps the prototype simple while the architecture supports easy migration to SQLite later.

## System Components

- **Frontend (React):** Task input, constraint configuration, utility weight sliders, schedule display
- **API Layer (FastAPI):** REST endpoints, request validation, response formatting
- **Orchestrator:** Coordinates the planning flow — calls categorizer → optimizer → returns schedule
- **Categorizer Module:** LLM-powered task classification (personal/work/health)
- **Optimizer Module:** Algorithm selection and execution (greedy/knapsack/permutation/llm)
- **State Manager:** JSON file read/write for tasks, schedules, user preferences

## File Structure

```
frontend/
  src/
    components/
      TaskInput.tsx
      ConstraintForm.tsx
      UtilityWeights.tsx
      ScheduleView.tsx
    App.tsx
    api.ts
    types.ts
  package.json
  vite.config.ts

backend/
  app/
    main.py
    orchestrator.py
    modules/
      categorizer.py
      optimizer.py
    state/
      manager.py
      data.json
    models.py
    config.py
  requirements.txt
  .env.example

tests/
  backend/
    test_categorizer.py
    test_optimizer.py
    test_orchestrator.py
```

## Feature Roadmap (Priority Order)

### Phase 1 - Bootstrap (Get it running)
1. Project scaffolding (React + FastAPI structure)
2. Basic API health check and frontend-backend connection
3. Static task input form → display submitted tasks

### Phase 2 - Core Flow
4. LLM categorization module (OpenAI integration)
5. Orchestrator with categorization step
6. Constraint input UI (available hours, deadlines)
7. Utility weight configuration UI

### Phase 3 - Optimization
8. Greedy optimizer (simplest case)
9. Knapsack optimizer (capacity-constrained)
10. Permutation optimizer (order-dependent)
11. LLM fallback optimizer
12. Algorithm selection logic
13. Schedule display component

### Phase 4 - Persistence & Polish
14. SQLite database migration
15. Save/load previous schedules
16. User preferences persistence

### Phase 5 - Integrations
17. Calendar export (iCal format)
18. Google Calendar integration

## Production Considerations

**Security:** API key stored in .env (never committed). Input sanitization on task text. Rate limiting on LLM calls.

**Error Handling:** Graceful fallback if OpenAI fails (use LLM optimizer as backup categorizer or show manual categorization UI). Validation errors returned with clear messages.

**Logging:** Log orchestrator flow steps, optimizer selection reasoning, LLM token usage. JSON logs for prototype, structured logging for production.

**Performance:** Cache categorization results during session. Optimizer timeout with fallback to simpler algorithm.

## Data Model

```python
Task:
  id: str (uuid)
  text: str
  category: "personal" | "work" | "health" | null
  duration_minutes: int | null
  deadline: datetime | null
  confirmed: bool

Constraints:
  available_blocks: list[TimeBlock]  # e.g., [(9:00, 12:00), (13:00, 17:00)]
  category_weights: dict[str, float]  # e.g., {"work": 0.5, "personal": 0.3, "health": 0.2}

Schedule:
  id: str (uuid)
  created_at: datetime
  tasks: list[ScheduledTask]

ScheduledTask:
  task_id: str
  start_time: datetime
  end_time: datetime
  category: str
```

## API Design

```
POST /api/tasks
  Body: { tasks: string[] }
  Response: { tasks: Task[] }

POST /api/categorize
  Body: { task_ids: string[] }
  Response: { tasks: Task[] }  # with categories filled

POST /api/constraints
  Body: Constraints
  Response: { saved: true }

POST /api/optimize
  Body: { task_ids: string[], constraints: Constraints }
  Response: { schedule: Schedule, algorithm_used: string }

GET /api/schedule
  Response: { schedule: Schedule | null }

GET /api/health
  Response: { status: "ok" }
```

## Orchestrator Flow

```
1. User submits tasks (text) → stored in state
2. Orchestrator calls Categorizer → tasks get categories
3. User confirms/adjusts categories, sets constraints + weights
4. Orchestrator calls Optimizer with:
   - tasks (with categories, durations)
   - constraints (time blocks, deadlines)
   - weights (category utilities)
5. Optimizer selects algorithm based on constraint complexity:
   - Simple (no deadlines, single block) → Greedy
   - Capacity-limited → Knapsack
   - Order-dependent / complex → Permutation
   - Edge cases / failures → LLM fallback
6. Schedule returned and displayed
```
