"""Tests for the GitHub model sources module."""

# from unittest.mock import MagicMock, patch

# import pytest

from ai_model_catalog.model_sources.github_model import RepositoryHandler


def test_repository_handler_initialization():
    """Test RepositoryHandler initialization."""
    handler = RepositoryHandler("test_owner", "test_repo")
    assert handler.owner == "test_owner"
    assert handler.repo == "test_repo"


def test_repository_handler_fetch_data(monkeypatch):
    """Test RepositoryHandler fetch_data method."""
    mock_data = {
        "full_name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "open_issues": 5,
        "license": {"spdx_id": "mit"},
        "updated_at": "2024-01-01T00:00:00Z",
    }

    with patch(
        "ai_model_catalog.model_sources.github_model.fetch_repo_data"
    ) as mock_fetch:
        mock_fetch.return_value = mock_data

        handler = RepositoryHandler("test_owner", "test_repo")
        result = handler.fetch_data()

        mock_fetch.assert_called_once_with(owner="test_owner", repo="test_repo")
        assert result == mock_data


def test_repository_handler_format_data(monkeypatch):
    """Test RepositoryHandler format_data method."""
    mock_data = {
        "full_name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "open_issues": 5,
        "license": {"spdx_id": "mit"},
        "updated_at": "2024-01-01T00:00:00Z",
    }

    mock_formatted = {
        "name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "issues": 5,
        "license": "mit",
        "updated": "2024-01-01T00:00:00Z",
    }

    with patch(
        "ai_model_catalog.model_sources.github_model._format_repository_data"
    ) as mock_format:
        mock_format.return_value = mock_formatted

        handler = RepositoryHandler("test_owner", "test_repo")
        result = handler.format_data(mock_data)

        mock_format.assert_called_once_with(mock_data, "test_owner", "test_repo")
        assert result == mock_formatted


def test_repository_handler_display_data(monkeypatch):
    """Test RepositoryHandler display_data method."""
    mock_data = {
        "full_name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "open_issues": 5,
        "license": {"spdx_id": "mit"},
        "updated_at": "2024-01-01T00:00:00Z",
    }

    mock_formatted = {
        "name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "issues": 5,
        "license": "mit",
        "updated": "2024-01-01T00:00:00Z",
    }

    mock_scores = {
        "NetScore": 0.85,
        "ramp_up_time": 1.0,
        "bus_factor": 1.0,
        "performance_claims": 0.5,
        "license": 1.0,
        "size": {
            "raspberry_pi": 0.2,
            "jetson_nano": 0.4,
            "desktop_pc": 0.8,
            "aws_server": 0.9,
        },
        "availability": 1.0,
        "dataset_quality": 0.75,
        "code_quality": 0.5,
    }

    with (
        patch(
            "ai_model_catalog.model_sources.github_model._get_repository_counts_info"
        ) as mock_counts,
        patch(
            "ai_model_catalog.model_sources.github_model._display_repository_info"
        ) as mock_display_info,
        patch(
            "ai_model_catalog.model_sources.github_model.score_repo_from_owner_and_repo"
        ) as mock_score,
        patch(
            "ai_model_catalog.model_sources.github_model._display_scores"
        ) as mock_display_scores,
    ):

        mock_counts.return_value = {"commits": 100, "contributors": 10}
        mock_score.return_value = mock_scores

        handler = RepositoryHandler("test_owner", "test_repo")
        handler.display_data(mock_formatted, mock_data)

        # Verify all methods were called
        mock_counts.assert_called_once_with(mock_data)
        mock_display_info.assert_called_once_with(
            mock_formatted, {"commits": 100, "contributors": 10}
        )
        mock_score.assert_called_once_with("test_owner", "test_repo")
        mock_display_scores.assert_called_once_with(mock_scores)


def test_repository_handler_inheritance():
    """Test that RepositoryHandler inherits from BaseHandler."""
    handler = RepositoryHandler("test_owner", "test_repo")

    # Check inheritance
    from ai_model_catalog.model_sources.base import BaseHandler

    assert isinstance(handler, BaseHandler)

    # Check that all required methods exist
    assert hasattr(handler, "fetch_data")
    assert hasattr(handler, "format_data")
    assert hasattr(handler, "display_data")

    # Check that methods are callable
    assert callable(handler.fetch_data)
    assert callable(handler.format_data)
    assert callable(handler.display_data)
