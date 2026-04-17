"""Optimization algorithms for task scheduling."""
import json
import logging
from datetime import datetime, timedelta
from itertools import permutations
from typing import Optional

from openai import OpenAI

from ..config import OPENAI_API_KEY
from ..models import Constraints, FixedTimeConstraint, ScheduledTask, Task, TimeBlock

logger = logging.getLogger(__name__)


def _parse_time(time_str: str, base_date: datetime) -> datetime:
    """Parse time string (HH:MM) into datetime with base date."""
    hours, minutes = map(int, time_str.split(":"))
    return base_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)


def _get_available_minutes(blocks: list[TimeBlock], base_date: datetime) -> int:
    """Calculate total available minutes from time blocks."""
    total = 0
    for block in blocks:
        start = _parse_time(block.start, base_date)
        end = _parse_time(block.end, base_date)
        total += int((end - start).total_seconds() / 60)
    return total


def _calculate_task_utility(task: Task, weights: dict[str, float]) -> float:
    """Calculate utility score for a task based on category weights."""
    category = task.category or "personal"
    return weights.get(category, 0.3)


def greedy_optimize(
    tasks: list[Task], constraints: Constraints, base_date: datetime
) -> list[ScheduledTask]:
    """
    Greedy optimizer: Schedule tasks in order of highest utility.
    Simple approach - picks highest value tasks first.
    """
    if not tasks or not constraints.available_blocks:
        return []

    # Sort tasks by utility (highest first)
    sorted_tasks = sorted(
        tasks,
        key=lambda t: _calculate_task_utility(t, constraints.category_weights),
        reverse=True,
    )

    scheduled = []
    current_block_idx = 0
    current_time = _parse_time(constraints.available_blocks[0].start, base_date)
    block_end = _parse_time(constraints.available_blocks[0].end, base_date)

    for task in sorted_tasks:
        duration = task.duration_minutes or 30

        # Check if task fits in current block
        task_end = current_time + timedelta(minutes=duration)

        if task_end <= block_end:
            # Task fits
            scheduled.append(
                ScheduledTask(
                    task_id=task.id,
                    start_time=current_time,
                    end_time=task_end,
                    category=task.category or "personal",
                )
            )
            current_time = task_end
        else:
            # Try next block
            current_block_idx += 1
            if current_block_idx >= len(constraints.available_blocks):
                break  # No more blocks

            current_time = _parse_time(
                constraints.available_blocks[current_block_idx].start, base_date
            )
            block_end = _parse_time(
                constraints.available_blocks[current_block_idx].end, base_date
            )

            task_end = current_time + timedelta(minutes=duration)
            if task_end <= block_end:
                scheduled.append(
                    ScheduledTask(
                        task_id=task.id,
                        start_time=current_time,
                        end_time=task_end,
                        category=task.category or "personal",
                    )
                )
                current_time = task_end

    return scheduled


def knapsack_optimize(
    tasks: list[Task], constraints: Constraints, base_date: datetime
) -> list[ScheduledTask]:
    """
    Knapsack optimizer: Maximize total utility within time capacity.
    Uses 0/1 knapsack dynamic programming approach.
    """
    if not tasks or not constraints.available_blocks:
        return []

    total_capacity = _get_available_minutes(constraints.available_blocks, base_date)

    # Build value and weight arrays
    n = len(tasks)
    values = [_calculate_task_utility(t, constraints.category_weights) for t in tasks]
    weights = [t.duration_minutes or 30 for t in tasks]

    # DP table
    dp = [[0.0] * (total_capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(total_capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    dp[i - 1][w], dp[i - 1][w - weights[i - 1]] + values[i - 1]
                )
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrack to find selected tasks
    selected_indices = []
    w = total_capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_indices.append(i - 1)
            w -= weights[i - 1]

    selected_indices.reverse()
    selected_tasks = [tasks[i] for i in selected_indices]

    # Schedule selected tasks using greedy placement
    return _place_tasks_in_blocks(selected_tasks, constraints, base_date)


def _place_tasks_in_blocks(
    tasks: list[Task], constraints: Constraints, base_date: datetime
) -> list[ScheduledTask]:
    """Place a list of tasks into available time blocks."""
    if not tasks or not constraints.available_blocks:
        return []

    scheduled = []
    current_block_idx = 0
    current_time = _parse_time(constraints.available_blocks[0].start, base_date)
    block_end = _parse_time(constraints.available_blocks[0].end, base_date)

    for task in tasks:
        duration = task.duration_minutes or 30
        task_end = current_time + timedelta(minutes=duration)

        # Find a block where the task fits
        while task_end > block_end:
            current_block_idx += 1
            if current_block_idx >= len(constraints.available_blocks):
                return scheduled  # No more blocks

            current_time = _parse_time(
                constraints.available_blocks[current_block_idx].start, base_date
            )
            block_end = _parse_time(
                constraints.available_blocks[current_block_idx].end, base_date
            )
            task_end = current_time + timedelta(minutes=duration)

        scheduled.append(
            ScheduledTask(
                task_id=task.id,
                start_time=current_time,
                end_time=task_end,
                category=task.category or "personal",
            )
        )
        current_time = task_end

    return scheduled


def _minutes_to_time(minutes: int, base_date: datetime) -> datetime:
    """Convert minutes from start of day to datetime."""
    hours = minutes // 60
    mins = minutes % 60
    return base_date.replace(hour=hours, minute=mins, second=0, microsecond=0)


def _time_to_minutes(dt: datetime) -> int:
    """Convert datetime to minutes from start of day."""
    return dt.hour * 60 + dt.minute


def _is_slot_available(
    start_time: datetime,
    end_time: datetime,
    scheduled: list[ScheduledTask],
    constraints: Constraints,
    base_date: datetime,
) -> bool:
    """Check if a time slot is available (within blocks and not overlapping)."""
    # Check if slot is within any available block
    in_block = False
    for block in constraints.available_blocks:
        block_start = _parse_time(block.start, base_date)
        block_end = _parse_time(block.end, base_date)
        if start_time >= block_start and end_time <= block_end:
            in_block = True
            break

    if not in_block:
        return False

    # Check for overlaps with already scheduled tasks
    for st in scheduled:
        if not (end_time <= st.start_time or start_time >= st.end_time):
            return False

    return True


def _place_tasks_with_fixed_constraints(
    tasks: list[Task], constraints: Constraints, base_date: datetime
) -> tuple[list[ScheduledTask], list[Task]]:
    """
    Place tasks that have fixed time constraints first.
    Returns (scheduled_fixed_tasks, remaining_tasks_without_fixed_constraints).
    """
    scheduled = []
    remaining = []

    for task in tasks:
        if task.fixed_time_constraint:
            ftc = task.fixed_time_constraint
            duration = task.duration_minutes or 30

            # The fixed constraint defines a window - place task at the start of window
            task_start = _minutes_to_time(ftc.start_minutes, base_date)
            task_end = task_start + timedelta(minutes=duration)

            # Verify the task fits within the constraint window
            window_end = _minutes_to_time(ftc.end_minutes, base_date)
            if task_end > window_end:
                # Task doesn't fit in window, try to fit it anyway at start
                logger.warning(
                    f"Task {task.id} duration exceeds fixed time window, placing at window start"
                )

            # Check if this slot is available
            if _is_slot_available(task_start, task_end, scheduled, constraints, base_date):
                scheduled.append(
                    ScheduledTask(
                        task_id=task.id,
                        start_time=task_start,
                        end_time=task_end,
                        category=task.category or "personal",
                    )
                )
            else:
                logger.warning(
                    f"Fixed time constraint for task {task.id} conflicts, skipping constraint"
                )
                remaining.append(task)
        else:
            remaining.append(task)

    return scheduled, remaining


def _place_tasks_around_fixed(
    tasks: list[Task],
    fixed_scheduled: list[ScheduledTask],
    constraints: Constraints,
    base_date: datetime,
) -> list[ScheduledTask]:
    """Place remaining tasks around already-scheduled fixed tasks."""
    scheduled = list(fixed_scheduled)

    if not tasks:
        return scheduled

    # Build list of available slots (gaps between fixed tasks and block boundaries)
    available_slots = []

    for block in constraints.available_blocks:
        block_start = _parse_time(block.start, base_date)
        block_end = _parse_time(block.end, base_date)

        # Find fixed tasks in this block
        fixed_in_block = [
            st for st in fixed_scheduled
            if st.start_time >= block_start and st.end_time <= block_end
        ]
        fixed_in_block.sort(key=lambda st: st.start_time)

        # Create slots around fixed tasks
        current = block_start
        for fixed in fixed_in_block:
            if current < fixed.start_time:
                available_slots.append((current, fixed.start_time))
            current = fixed.end_time

        if current < block_end:
            available_slots.append((current, block_end))

    # Place tasks in available slots
    for task in tasks:
        duration = task.duration_minutes or 30
        placed = False

        for i, (slot_start, slot_end) in enumerate(available_slots):
            slot_duration = int((slot_end - slot_start).total_seconds() / 60)

            if slot_duration >= duration:
                task_end = slot_start + timedelta(minutes=duration)
                scheduled.append(
                    ScheduledTask(
                        task_id=task.id,
                        start_time=slot_start,
                        end_time=task_end,
                        category=task.category or "personal",
                    )
                )
                # Update the slot
                if task_end < slot_end:
                    available_slots[i] = (task_end, slot_end)
                else:
                    available_slots.pop(i)
                placed = True
                break

        if not placed:
            logger.debug(f"Could not place task {task.id} in any available slot")

    # Sort by start time
    scheduled.sort(key=lambda st: st.start_time)
    return scheduled


def permutation_optimize(
    tasks: list[Task], constraints: Constraints, base_date: datetime
) -> list[ScheduledTask]:
    """
    Permutation optimizer: Try all orderings to find optimal schedule.
    Best for small task sets (<=8 tasks due to factorial complexity).

    This is the ONLY optimizer that respects fixed time constraints.
    Tasks with fixed time constraints are placed first at their specified times,
    then remaining tasks are permuted to find the optimal arrangement.
    """
    if not tasks or not constraints.available_blocks:
        return []

    # First, place tasks with fixed time constraints
    fixed_scheduled, remaining_tasks = _place_tasks_with_fixed_constraints(
        tasks, constraints, base_date
    )

    # If no remaining tasks, just return fixed tasks
    if not remaining_tasks:
        return fixed_scheduled

    # Limit remaining tasks to prevent combinatorial explosion
    MAX_TASKS = 8
    if len(remaining_tasks) > MAX_TASKS:
        logger.warning(
            f"Too many tasks ({len(remaining_tasks)}) for permutation, using greedy for remaining"
        )
        return _place_tasks_around_fixed(remaining_tasks, fixed_scheduled, constraints, base_date)

    best_schedule = fixed_scheduled
    best_utility = sum(
        constraints.category_weights.get(st.category, 0.3)
        for st in fixed_scheduled
    )

    for perm in permutations(remaining_tasks):
        schedule = _place_tasks_around_fixed(
            list(perm), fixed_scheduled, constraints, base_date
        )

        # Calculate total utility of this schedule
        total_utility = sum(
            constraints.category_weights.get(st.category, 0.3)
            for st in schedule
        )

        if total_utility > best_utility:
            best_utility = total_utility
            best_schedule = schedule

    return best_schedule


def llm_optimize(
    tasks: list[Task], constraints: Constraints, base_date: datetime
) -> list[ScheduledTask]:
    """
    LLM optimizer: Use OpenAI to suggest optimal task ordering.
    Fallback for complex scenarios or edge cases.
    """
    if not tasks or not constraints.available_blocks:
        return []

    if not OPENAI_API_KEY:
        logger.warning("No OpenAI API key, falling back to greedy")
        return greedy_optimize(tasks, constraints, base_date)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Build prompt
        task_list = "\n".join(
            f"- {t.text} (category: {t.category}, duration: {t.duration_minutes}min)"
            for t in tasks
        )
        blocks_list = "\n".join(
            f"- {b.start} to {b.end}" for b in constraints.available_blocks
        )
        weights_str = ", ".join(
            f"{k}: {v}" for k, v in constraints.category_weights.items()
        )

        prompt = f"""Schedule these tasks optimally:

Tasks:
{task_list}

Available time blocks:
{blocks_list}

Category priorities (weights): {weights_str}

Return ONLY a JSON array with task IDs in optimal order, like:
["task-id-1", "task-id-2", ...]

Consider:
1. Higher weight categories should be prioritized
2. Try to fit all tasks within available blocks
3. Group similar categories when possible
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response")

        # Parse the task order
        task_order = json.loads(content.strip())

        # Reorder tasks according to LLM suggestion
        task_map = {t.id: t for t in tasks}
        ordered_tasks = [task_map[tid] for tid in task_order if tid in task_map]

        # Add any tasks that weren't in the LLM response
        for task in tasks:
            if task not in ordered_tasks:
                ordered_tasks.append(task)

        return _place_tasks_in_blocks(ordered_tasks, constraints, base_date)

    except Exception as e:
        logger.error(f"LLM optimization failed: {e}, falling back to greedy")
        return greedy_optimize(tasks, constraints, base_date)


def select_algorithm(
    tasks: list[Task], constraints: Constraints
) -> str:
    """
    Select the best algorithm based on constraint complexity.

    Returns: "greedy", "knapsack", "permutation", or "llm"
    """
    num_tasks = len(tasks)
    num_blocks = len(constraints.available_blocks)
    has_deadlines = any(t.deadline for t in tasks)
    has_fixed_constraints = any(t.fixed_time_constraint for t in tasks)

    # IMPORTANT: If any task has fixed time constraints, MUST use permutation
    # (only permutation optimizer respects fixed time constraints)
    if has_fixed_constraints:
        logger.info("Fixed time constraints detected, forcing permutation optimizer")
        return "permutation"

    # Simple case: few tasks, single block, no deadlines -> greedy
    if num_tasks <= 3 and num_blocks == 1 and not has_deadlines:
        return "greedy"

    # Small task set with multiple constraints -> permutation
    if num_tasks <= 8 and (num_blocks > 1 or has_deadlines):
        return "permutation"

    # Capacity-limited (need to select subset) -> knapsack
    total_task_time = sum(t.duration_minutes or 30 for t in tasks)
    total_available = sum(
        60  # Rough estimate per block
        for _ in constraints.available_blocks
    )
    if total_task_time > total_available * 1.5:
        return "knapsack"

    # Complex cases -> LLM
    if has_deadlines or num_blocks > 2:
        return "llm"

    # Default to greedy
    return "greedy"


def optimize(
    tasks: list[Task], constraints: Constraints, algorithm: Optional[str] = None
) -> tuple[list[ScheduledTask], str]:
    """
    Main optimization entry point.

    Args:
        tasks: List of tasks to schedule
        constraints: Time blocks and category weights
        algorithm: Force specific algorithm, or None for auto-select

    Returns:
        Tuple of (scheduled_tasks, algorithm_used)
    """
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if not tasks:
        return [], "none"

    if not constraints.available_blocks:
        return [], "none"

    # Select algorithm if not specified
    if algorithm is None:
        algorithm = select_algorithm(tasks, constraints)

    logger.info(f"Using {algorithm} optimizer for {len(tasks)} tasks")

    # Run selected algorithm
    if algorithm == "greedy":
        scheduled = greedy_optimize(tasks, constraints, base_date)
    elif algorithm == "knapsack":
        scheduled = knapsack_optimize(tasks, constraints, base_date)
    elif algorithm == "permutation":
        scheduled = permutation_optimize(tasks, constraints, base_date)
    elif algorithm == "llm":
        scheduled = llm_optimize(tasks, constraints, base_date)
    else:
        logger.warning(f"Unknown algorithm {algorithm}, using greedy")
        scheduled = greedy_optimize(tasks, constraints, base_date)
        algorithm = "greedy"

    return scheduled, algorithm
