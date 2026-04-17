import logging
import uuid
from datetime import datetime

from .models import Constraints, Schedule, Task
from .modules.categorizer import categorize_tasks
from .modules.optimizer import optimize
from .state import manager

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates the planning flow: categorization → optimization."""

    def categorize(self, task_ids: list[str]) -> list[Task]:
        """Run categorization on specified tasks."""
        all_tasks = manager.get_tasks()
        tasks_to_categorize = [t for t in all_tasks if t.id in task_ids]

        if not tasks_to_categorize:
            logger.warning(f"No tasks found for ids: {task_ids}")
            return []

        categorized = categorize_tasks(tasks_to_categorize)

        # Update tasks in state
        for task in categorized:
            manager.update_task(task.id, category=task.category, duration_minutes=task.duration_minutes)

        logger.info(f"Categorized {len(categorized)} tasks")
        return categorized

    def save_constraints(self, constraints: Constraints) -> bool:
        """Save user constraints for optimization."""
        manager.save_constraints(constraints)
        logger.info("Constraints saved")
        return True

    def get_constraints(self) -> Constraints | None:
        """Get saved constraints."""
        return manager.get_constraints()

    def optimize(
        self, task_ids: list[str], constraints: Constraints | None = None
    ) -> tuple[Schedule, str]:
        """
        Run optimization on specified tasks.

        Args:
            task_ids: IDs of tasks to schedule
            constraints: Optional constraints (uses saved if not provided)

        Returns:
            Tuple of (schedule, algorithm_used)
        """
        # Get tasks
        all_tasks = manager.get_tasks()
        tasks_to_optimize = [t for t in all_tasks if t.id in task_ids]

        if not tasks_to_optimize:
            logger.warning(f"No tasks found for optimization: {task_ids}")
            empty_schedule = Schedule(
                id=str(uuid.uuid4()),
                created_at=datetime.now(),
                tasks=[],
            )
            return empty_schedule, "none"

        # Get constraints
        if constraints is None:
            constraints = manager.get_constraints()

        if constraints is None:
            logger.warning("No constraints available for optimization")
            empty_schedule = Schedule(
                id=str(uuid.uuid4()),
                created_at=datetime.now(),
                tasks=[],
            )
            return empty_schedule, "none"

        # Run optimization
        scheduled_tasks, algorithm = optimize(tasks_to_optimize, constraints)

        # Create schedule
        schedule = Schedule(
            id=str(uuid.uuid4()),
            created_at=datetime.now(),
            tasks=scheduled_tasks,
        )

        # Save schedule
        manager.save_schedule(schedule)

        logger.info(
            f"Optimized {len(tasks_to_optimize)} tasks into {len(scheduled_tasks)} "
            f"scheduled slots using {algorithm}"
        )
        return schedule, algorithm

    def get_schedule(self) -> Schedule | None:
        """Get saved schedule."""
        return manager.get_schedule()


orchestrator = Orchestrator()
