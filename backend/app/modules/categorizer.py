import json
import logging

from openai import OpenAI

from ..config import OPENAI_API_KEY
from ..models import Task

logger = logging.getLogger(__name__)

CATEGORIES = ["personal", "work", "health"]

SYSTEM_PROMPT = """You are a task categorizer. Categorize each task into one of these categories: personal, work, health.

Rules:
- "personal" = household, family, social, hobbies, errands
- "work" = job tasks, meetings, professional development, emails
- "health" = exercise, medical, nutrition, mental health, sleep

Also estimate duration in minutes (15-480 range, in 15-min increments).

Respond with JSON array: [{"text": "task text", "category": "category", "duration_minutes": number}]
Only return valid JSON, no other text."""


def categorize_tasks(tasks: list[Task]) -> list[Task]:
    """Categorize tasks using OpenAI API."""
    if not tasks:
        return []

    if not OPENAI_API_KEY:
        logger.warning("No OpenAI API key configured, using fallback categorization")
        return _fallback_categorize(tasks)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        task_texts = [t.text for t in tasks]
        user_message = "Categorize these tasks:\n" + "\n".join(f"- {t}" for t in task_texts)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        if not content:
            logger.error("Empty response from OpenAI")
            return _fallback_categorize(tasks)

        categorized = json.loads(content)

        # Map results back to tasks
        result = []
        for task in tasks:
            matching = next(
                (c for c in categorized if c.get("text", "").lower() == task.text.lower()),
                None
            )
            if matching:
                task.category = matching.get("category", "personal")
                task.duration_minutes = matching.get("duration_minutes", 30)
            else:
                # Fallback if no match found
                task.category = "personal"
                task.duration_minutes = 30
            result.append(task)

        logger.info(f"Categorized {len(result)} tasks via OpenAI")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response: {e}")
        return _fallback_categorize(tasks)
    except Exception as e:
        logger.error(f"OpenAI categorization failed: {e}")
        return _fallback_categorize(tasks)


def _fallback_categorize(tasks: list[Task]) -> list[Task]:
    """Simple keyword-based fallback categorization."""
    work_keywords = ["meeting", "email", "report", "project", "deadline", "client", "presentation", "review", "call"]
    health_keywords = ["gym", "workout", "doctor", "exercise", "run", "yoga", "meditation", "sleep", "eat", "meal"]

    for task in tasks:
        text_lower = task.text.lower()
        if any(kw in text_lower for kw in health_keywords):
            task.category = "health"
            task.duration_minutes = 45
        elif any(kw in text_lower for kw in work_keywords):
            task.category = "work"
            task.duration_minutes = 60
        else:
            task.category = "personal"
            task.duration_minutes = 30

    return tasks
