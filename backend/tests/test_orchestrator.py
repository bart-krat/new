"""Tests for the orchestrator module."""
import pytest
from unittest.mock import patch, MagicMock
from app.orchestrator import Orchestrator, orchestrator
from app.models import Task, Constraints, TimeBlock


@pytest.fixture
def orch():
    """Create a fresh orchestrator instance."""
    return Orchestrator()


class TestOrchestratorCategorize:
    """Tests for orchestrator categorization."""

    @patch("app.orchestrator.manager")
    @patch("app.orchestrator.categorize_tasks")
    def test_categorize_fetches_tasks_by_id(self, mock_categorize, mock_manager, orch):
        """Categorize fetches tasks from state by ID."""
        mock_manager.get_tasks.return_value = [
            Task(id="1", text="Task 1"),
            Task(id="2", text="Task 2"),
            Task(id="3", text="Task 3"),
        ]
        mock_categorize.return_value = [Task(id="1", text="Task 1", category="work")]

        result = orch.categorize(["1"])

        mock_manager.get_tasks.assert_called_once()
        # Should only pass matching tasks to categorizer
        mock_categorize.assert_called_once()
        call_args = mock_categorize.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0].id == "1"

    @patch("app.orchestrator.manager")
    @patch("app.orchestrator.categorize_tasks")
    def test_categorize_updates_state(self, mock_categorize, mock_manager, orch):
        """Categorized tasks are updated in state."""
        mock_manager.get_tasks.return_value = [Task(id="1", text="Task 1")]
        categorized_task = Task(id="1", text="Task 1", category="work", duration_minutes=60)
        mock_categorize.return_value = [categorized_task]

        orch.categorize(["1"])

        mock_manager.update_task.assert_called_once_with(
            "1", category="work", duration_minutes=60
        )

    @patch("app.orchestrator.manager")
    def test_categorize_empty_ids_returns_empty(self, mock_manager, orch):
        """Empty task IDs returns empty list."""
        mock_manager.get_tasks.return_value = []

        result = orch.categorize([])

        assert result == []

    @patch("app.orchestrator.manager")
    def test_categorize_no_matching_tasks(self, mock_manager, orch):
        """Returns empty when no tasks match given IDs."""
        mock_manager.get_tasks.return_value = [Task(id="1", text="Task 1")]

        result = orch.categorize(["nonexistent"])

        assert result == []

    @patch("app.orchestrator.manager")
    @patch("app.orchestrator.categorize_tasks")
    def test_categorize_multiple_tasks(self, mock_categorize, mock_manager, orch):
        """Can categorize multiple tasks at once."""
        mock_manager.get_tasks.return_value = [
            Task(id="1", text="Task 1"),
            Task(id="2", text="Task 2"),
        ]
        mock_categorize.return_value = [
            Task(id="1", text="Task 1", category="work", duration_minutes=30),
            Task(id="2", text="Task 2", category="health", duration_minutes=45),
        ]

        result = orch.categorize(["1", "2"])

        assert len(result) == 2
        assert mock_manager.update_task.call_count == 2


class TestOrchestratorConstraints:
    """Tests for orchestrator constraints handling."""

    @patch("app.orchestrator.manager")
    def test_save_constraints(self, mock_manager, orch):
        """Saves constraints to state."""
        constraints = Constraints(
            available_blocks=[TimeBlock(start="09:00", end="17:00")],
            category_weights={"work": 0.5, "personal": 0.3, "health": 0.2},
        )

        result = orch.save_constraints(constraints)

        assert result is True
        mock_manager.save_constraints.assert_called_once_with(constraints)

    @patch("app.orchestrator.manager")
    def test_get_constraints_returns_saved(self, mock_manager, orch):
        """Returns saved constraints."""
        expected = Constraints(
            available_blocks=[TimeBlock(start="09:00", end="17:00")],
            category_weights={"work": 0.5, "personal": 0.3, "health": 0.2},
        )
        mock_manager.get_constraints.return_value = expected

        result = orch.get_constraints()

        assert result == expected
        mock_manager.get_constraints.assert_called_once()

    @patch("app.orchestrator.manager")
    def test_get_constraints_returns_none_when_empty(self, mock_manager, orch):
        """Returns None when no constraints saved."""
        mock_manager.get_constraints.return_value = None

        result = orch.get_constraints()

        assert result is None


class TestOrchestratorSingleton:
    """Tests for the orchestrator singleton instance."""

    def test_singleton_exists(self):
        """Module-level orchestrator instance exists."""
        assert orchestrator is not None
        assert isinstance(orchestrator, Orchestrator)
