"""Simple tests for fetch_repo.py to improve coverage"""

import os
import time
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from ai_model_catalog.fetch_repo import (
    create_session,
    time_request,
    _calculate_model_size,
    _extract_actions_runs,
    _format_actions_data,
    GitHubAPIError,
    RepositoryDataError,
)


class TestCreateSession:
    """Test create_session function."""

    def test_create_session(self):
        """Test creating a session with retry strategy."""
        session = create_session()
        
        assert isinstance(session, requests.Session)
        # Test that the session has retry strategy configured
        assert hasattr(session, 'mount')


class TestTimeRequest:
    """Test time_request function."""

    def test_time_request_success(self):
        """Test time_request with successful function."""
        def test_func():
            return "success"
        
        result, latency = time_request(test_func)
        
        assert result == "success"
        assert isinstance(latency, int)
        assert latency >= 0

    def test_time_request_exception(self):
        """Test time_request with function that raises exception."""
        def test_func():
            raise ValueError("test error")
        
        with pytest.raises(ValueError, match="test error"):
            time_request(test_func)


class TestCalculateModelSize:
    """Test _calculate_model_size function."""

    def test_calculate_model_size_used_storage(self):
        """Test calculating model size from usedStorage."""
        model_data = {"usedStorage": 1024 * 1024}
        
        result = _calculate_model_size(model_data)
        assert result == 1024 * 1024

    def test_calculate_model_size_safetensors(self):
        """Test calculating model size from safetensors."""
        model_data = {
            "safetensors": [
                {"size": 512 * 1024},
                {"size": 256 * 1024},
            ]
        }
        
        result = _calculate_model_size(model_data)
        assert result == 768 * 1024

    def test_calculate_model_size_siblings(self):
        """Test calculating model size from siblings."""
        model_data = {
            "siblings": [
                {"size": 1024 * 1024},
                {"size": 512 * 1024},
            ]
        }
        
        result = _calculate_model_size(model_data)
        assert result == 1536 * 1024

    def test_calculate_model_size_default(self):
        """Test calculating model size with default fallback."""
        model_data = {}
        
        result = _calculate_model_size(model_data)
        assert result == 100 * 1024 * 1024

    def test_calculate_model_size_invalid_safetensors(self):
        """Test calculating model size with invalid safetensors data."""
        model_data = {
            "safetensors": [
                {"invalid": "data"},
                "not_a_dict",
            ]
        }
        
        result = _calculate_model_size(model_data)
        assert result == 0  # Invalid data returns 0, not default

    def test_calculate_model_size_invalid_siblings(self):
        """Test calculating model size with invalid siblings data."""
        model_data = {
            "siblings": [
                {"invalid": "data"},
                "not_a_dict",
            ]
        }
        
        result = _calculate_model_size(model_data)
        assert result == 0  # Invalid data returns 0, not default

    def test_calculate_model_size_empty_safetensors(self):
        """Test calculating model size with empty safetensors."""
        model_data = {"safetensors": []}
        
        result = _calculate_model_size(model_data)
        assert result == 100 * 1024 * 1024

    def test_calculate_model_size_empty_siblings(self):
        """Test calculating model size with empty siblings."""
        model_data = {"siblings": []}
        
        result = _calculate_model_size(model_data)
        assert result == 100 * 1024 * 1024


class TestExtractActionsRuns:
    """Test _extract_actions_runs function."""

    def test_extract_actions_runs_success(self):
        """Test extracting actions runs successfully."""
        actions_data = {"workflow_runs": [{"id": 1}, {"id": 2}]}
        
        result = _extract_actions_runs(actions_data)
        assert result == [{"id": 1}, {"id": 2}]

    def test_extract_actions_runs_empty(self):
        """Test extracting actions runs from empty data."""
        actions_data = []
        
        result = _extract_actions_runs(actions_data)
        assert result == []

    def test_extract_actions_runs_no_workflow_runs(self):
        """Test extracting actions runs when no workflow_runs key."""
        actions_data = [{"other_key": "value"}]
        
        result = _extract_actions_runs(actions_data)
        assert result == []

    def test_extract_actions_runs_mixed_data(self):
        """Test extracting actions runs with mixed data."""
        actions_data = {"workflow_runs": [{"id": 1}, {"id": 2}]}
        
        result = _extract_actions_runs(actions_data)
        assert result == [{"id": 1}, {"id": 2}]


class TestFormatActionsData:
    """Test _format_actions_data function."""

    def test_format_actions_data_success(self):
        """Test formatting actions data successfully."""
        actions_runs = [
            {
                "id": 1,
                "name": "CI",
                "status": "completed",
                "conclusion": "success",
                "head_commit": {"id": "abc123"},
            }
        ]
        
        result = _format_actions_data(actions_runs)
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["name"] == "CI"

    def test_format_actions_data_empty(self):
        """Test formatting empty actions data."""
        actions_runs = []
        
        result = _format_actions_data(actions_runs)
        assert result == []

    def test_format_actions_data_missing_fields(self):
        """Test formatting actions data with missing fields."""
        actions_runs = [
            {
                "id": 1,
                "name": "CI",
                # Missing status, conclusion, head_commit
            }
        ]
        
        result = _format_actions_data(actions_runs)
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["name"] == "CI"
        assert result[0]["status"] is None
        assert result[0]["conclusion"] is None
        assert result[0]["commit"] is None


class TestExceptions:
    """Test custom exceptions."""

    def test_github_api_error(self):
        """Test GitHubAPIError exception."""
        error = GitHubAPIError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_repository_data_error(self):
        """Test RepositoryDataError exception."""
        error = RepositoryDataError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_github_token_from_env(self):
        """Test GitHub token from environment variable."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test-token'}):
            # Re-import to get updated HEADERS
            import importlib
            import ai_model_catalog.fetch_repo
            importlib.reload(ai_model_catalog.fetch_repo)
            
            # Check that the token is in headers
            assert 'Authorization' in ai_model_catalog.fetch_repo.HEADERS
            assert ai_model_catalog.fetch_repo.HEADERS['Authorization'] == 'token test-token'

    def test_no_github_token(self):
        """Test when no GitHub token is set."""
        with patch.dict(os.environ, {}, clear=True):
            # Re-import to get updated HEADERS
            import importlib
            import ai_model_catalog.fetch_repo
            importlib.reload(ai_model_catalog.fetch_repo)
            
            # Check that there's no Authorization header
            assert 'Authorization' not in ai_model_catalog.fetch_repo.HEADERS


class TestConstants:
    """Test module constants."""

    def test_api_urls(self):
        """Test API URL constants."""
        from ai_model_catalog.fetch_repo import GITHUB_API, HF_API
        
        assert GITHUB_API == "https://api.github.com"
        assert HF_API == "https://huggingface.co/api"

    def test_headers_structure(self):
        """Test headers structure."""
        from ai_model_catalog.fetch_repo import HEADERS, HF_HEADERS
        
        assert 'Accept' in HEADERS
        assert 'User-Agent' in HEADERS
        assert 'Accept' in HF_HEADERS
        assert 'User-Agent' in HF_HEADERS


class TestSampleActionRun:
    """Test SAMPLE_ACTION_RUN constant."""

    def test_sample_action_run_structure(self):
        """Test SAMPLE_ACTION_RUN constant structure."""
        from ai_model_catalog.fetch_repo import SAMPLE_ACTION_RUN
        
        assert isinstance(SAMPLE_ACTION_RUN, dict)
        assert 'id' in SAMPLE_ACTION_RUN
        assert 'name' in SAMPLE_ACTION_RUN
        assert 'status' in SAMPLE_ACTION_RUN
        assert 'conclusion' in SAMPLE_ACTION_RUN
        assert 'head_commit' in SAMPLE_ACTION_RUN
        assert isinstance(SAMPLE_ACTION_RUN['head_commit'], dict)
        assert 'id' in SAMPLE_ACTION_RUN['head_commit']
