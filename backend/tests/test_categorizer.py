"""Tests for the categorizer module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.models import Task
from app.modules.categorizer import categorize_tasks, _fallback_categorize, CATEGORIES


class TestFallbackCategorize:
    """Tests for keyword-based fallback categorization."""

    def test_categorizes_work_keywords(self):
        """Tasks with work keywords get work category."""
        tasks = [
            Task(id="1", text="Attend team meeting"),
            Task(id="2", text="Send email to client"),
            Task(id="3", text="Review project proposal"),
        ]
        result = _fallback_categorize(tasks)
        assert all(t.category == "work" for t in result)
        # Categorizer should not change duration - it stays at default 30
        assert all(t.duration_minutes == 30 for t in result)

    def test_categorizes_health_keywords(self):
        """Tasks with health keywords get health category."""
        tasks = [
            Task(id="1", text="Go to gym"),
            Task(id="2", text="Morning workout"),
            Task(id="3", text="Doctor appointment"),
            Task(id="4", text="Yoga session"),
        ]
        result = _fallback_categorize(tasks)
        assert all(t.category == "health" for t in result)
        # Categorizer should not change duration - it stays at default 30
        assert all(t.duration_minutes == 30 for t in result)

    def test_categorizes_personal_as_default(self):
        """Tasks without keywords default to personal."""
        tasks = [
            Task(id="1", text="Buy groceries"),
            Task(id="2", text="Visit mom"),
            Task(id="3", text="Pick up dry cleaning"),
        ]
        result = _fallback_categorize(tasks)
        assert all(t.category == "personal" for t in result)
        # Categorizer should not change duration - it stays at default 30
        assert all(t.duration_minutes == 30 for t in result)

    def test_handles_empty_list(self):
        """Empty task list returns empty."""
        result = _fallback_categorize([])
        assert result == []

    def test_case_insensitive_matching(self):
        """Keyword matching is case insensitive."""
        tasks = [
            Task(id="1", text="MEETING with boss"),
            Task(id="2", text="GYM session"),
        ]
        result = _fallback_categorize(tasks)
        assert result[0].category == "work"
        assert result[1].category == "health"

    def test_preserves_task_id_and_text(self):
        """Categorization preserves original task data."""
        task = Task(id="test-123", text="Go to gym")
        result = _fallback_categorize([task])
        assert result[0].id == "test-123"
        assert result[0].text == "Go to gym"


class TestCategorizeTasks:
    """Tests for main categorization function."""

    def test_empty_list_returns_empty(self):
        """Empty task list returns empty without API call."""
        result = categorize_tasks([])
        assert result == []

    @patch("app.modules.categorizer.OPENAI_API_KEY", None)
    def test_uses_fallback_when_no_api_key(self):
        """Falls back to keyword categorization when no API key."""
        tasks = [Task(id="1", text="Go to gym")]
        result = categorize_tasks(tasks)
        assert result[0].category == "health"

    @patch("app.modules.categorizer.OPENAI_API_KEY", "test-key")
    @patch("app.modules.categorizer.OpenAI")
    def test_calls_openai_api(self, mock_openai_class):
        """Calls OpenAI API when key is configured."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='[{"text": "Go to gym", "category": "health"}]'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        tasks = [Task(id="1", text="Go to gym")]
        result = categorize_tasks(tasks)

        mock_client.chat.completions.create.assert_called_once()
        assert result[0].category == "health"
        # Categorizer should not change duration - it stays at default 30
        assert result[0].duration_minutes == 30

    @patch("app.modules.categorizer.OPENAI_API_KEY", "test-key")
    @patch("app.modules.categorizer.OpenAI")
    def test_fallback_on_empty_response(self, mock_openai_class):
        """Falls back when OpenAI returns empty content."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=None))]
        mock_client.chat.completions.create.return_value = mock_response

        tasks = [Task(id="1", text="Go to gym")]
        result = categorize_tasks(tasks)

        # Should use fallback
        assert result[0].category == "health"

    @patch("app.modules.categorizer.OPENAI_API_KEY", "test-key")
    @patch("app.modules.categorizer.OpenAI")
    def test_fallback_on_invalid_json(self, mock_openai_class):
        """Falls back when OpenAI returns invalid JSON."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="not valid json"))]
        mock_client.chat.completions.create.return_value = mock_response

        tasks = [Task(id="1", text="Go to gym")]
        result = categorize_tasks(tasks)

        # Should use fallback
        assert result[0].category == "health"

    @patch("app.modules.categorizer.OPENAI_API_KEY", "test-key")
    @patch("app.modules.categorizer.OpenAI")
    def test_fallback_on_api_exception(self, mock_openai_class):
        """Falls back when OpenAI API raises exception."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        tasks = [Task(id="1", text="Go to gym")]
        result = categorize_tasks(tasks)

        # Should use fallback
        assert result[0].category == "health"

    @patch("app.modules.categorizer.OPENAI_API_KEY", "test-key")
    @patch("app.modules.categorizer.OpenAI")
    def test_handles_unmatched_tasks(self, mock_openai_class):
        """Tasks not found in response get default category."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        # Response doesn't match task text
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='[{"text": "different task", "category": "work", "duration_minutes": 30}]'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        tasks = [Task(id="1", text="Go to gym")]
        result = categorize_tasks(tasks)

        # Should get default fallback values
        assert result[0].category == "personal"
        assert result[0].duration_minutes == 30


class TestCategoriesConstant:
    """Tests for category definitions."""

    def test_categories_exist(self):
        """All expected categories are defined."""
        assert "personal" in CATEGORIES
        assert "work" in CATEGORIES
        assert "health" in CATEGORIES

    def test_exactly_three_categories(self):
        """Only three categories exist."""
        assert len(CATEGORIES) == 3
