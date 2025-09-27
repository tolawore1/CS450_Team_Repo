"""Comprehensive tests for fetch_repo.py"""

import os
import time
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from ai_model_catalog.fetch_repo import (
    create_session,
    time_request,
    _make_github_request,
    _extract_page_count_from_link_header,
    _get_total_count_from_link_header,
    _fetch_github_endpoint,
    _fetch_readme_content,
    _fetch_repository_counts,
    _fetch_repository_samples,
    _extract_actions_runs,
    _format_actions_data,
    _fetch_github_api_data,
    _format_repo_api_data,
    fetch_repo_data,
    _calculate_model_size,
    _fetch_hf_readme,
    fetch_model_data,
    fetch_hf_model,
    fetch_dataset_data,
    GitHubAPIError,
    RepositoryDataError,
)


class TestCreateSession:
    """Test create_session function."""

    def test_create_session(self):
        """Test creating a session with retry strategy."""
        session = create_session()
        
        assert isinstance(session, requests.Session)
        assert session.mounts.get("http://") is not None
        assert session.mounts.get("https://") is not None


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


class TestMakeGithubRequest:
    """Test _make_github_request function."""

    @patch('ai_model_catalog.fetch_repo.create_session')
    def test_make_github_request_success(self, mock_create_session):
        """Test successful GitHub request."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_session.get.return_value = mock_response
        mock_create_session.return_value = mock_session
        
        result = _make_github_request("https://api.github.com/test")
        
        assert result == mock_response
        mock_session.get.assert_called_once()

    @patch('ai_model_catalog.fetch_repo.create_session')
    def test_make_github_request_with_params(self, mock_create_session):
        """Test GitHub request with parameters."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_create_session.return_value = mock_session
        
        params = {"page": 1, "per_page": 10}
        _make_github_request("https://api.github.com/test", params)
        
        mock_session.get.assert_called_once_with(
            "https://api.github.com/test",
            headers=ANY,
            params=params,
            timeout=30
        )

    @patch('ai_model_catalog.fetch_repo.create_session')
    def test_make_github_request_404_error(self, mock_create_session):
        """Test GitHub request with 404 error."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_session.get.return_value = mock_response
        mock_create_session.return_value = mock_session
        
        with pytest.raises(GitHubAPIError, match="Repository not found"):
            _make_github_request("https://api.github.com/test")

    @patch('ai_model_catalog.fetch_repo.create_session')
    def test_make_github_request_403_error(self, mock_create_session):
        """Test GitHub request with 403 error."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_session.get.return_value = mock_response
        mock_create_session.return_value = mock_session
        
        with pytest.raises(GitHubAPIError, match="API rate limit exceeded"):
            _make_github_request("https://api.github.com/test")

    @patch('ai_model_catalog.fetch_repo.create_session')
    def test_make_github_request_500_error(self, mock_create_session):
        """Test GitHub request with 500 error."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_session.get.return_value = mock_response
        mock_create_session.return_value = mock_session
        
        with pytest.raises(GitHubAPIError, match="GitHub API error: 500"):
            _make_github_request("https://api.github.com/test")

    @patch('ai_model_catalog.fetch_repo.create_session')
    def test_make_github_request_connection_error(self, mock_create_session):
        """Test GitHub request with connection error."""
        mock_session = Mock()
        mock_session.get.side_effect = ConnectionError("Connection failed")
        mock_create_session.return_value = mock_session
        
        with pytest.raises(GitHubAPIError, match="Failed to connect to GitHub API"):
            _make_github_request("https://api.github.com/test")


class TestExtractPageCountFromLinkHeader:
    """Test _extract_page_count_from_link_header function."""

    def test_extract_page_count_valid_header(self):
        """Test extracting page count from valid link header."""
        link_header = '<https://api.github.com/repos/test/repo/issues?page=2>; rel="next", <https://api.github.com/repos/test/repo/issues?page=5>; rel="last"'
        
        result = _extract_page_count_from_link_header(link_header)
        assert result == 5

    def test_extract_page_count_no_last(self):
        """Test extracting page count when no 'last' link."""
        link_header = '<https://api.github.com/repos/test/repo/issues?page=2>; rel="next"'
        
        result = _extract_page_count_from_link_header(link_header)
        assert result == 1

    def test_extract_page_count_invalid_header(self):
        """Test extracting page count from invalid header."""
        link_header = "invalid header"
        
        result = _extract_page_count_from_link_header(link_header)
        assert result == 1


class TestGetTotalCountFromLinkHeader:
    """Test _get_total_count_from_link_header function."""

    @patch('ai_model_catalog.fetch_repo._make_github_request')
    def test_get_total_count_success(self, mock_request):
        """Test getting total count successfully."""
        mock_response = Mock()
        mock_response.headers = {
            'Link': '<https://api.github.com/repos/test/repo/issues?page=1>; rel="prev", <https://api.github.com/repos/test/repo/issues?page=3>; rel="last"'
        }
        mock_request.return_value = mock_response
        
        result = _get_total_count_from_link_header("https://api.github.com/test")
        assert result == 3

    @patch('ai_model_catalog.fetch_repo._make_github_request')
    def test_get_total_count_no_link_header(self, mock_request):
        """Test getting total count when no link header."""
        mock_response = Mock()
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        result = _get_total_count_from_link_header("https://api.github.com/test")
        assert result == 1


class TestFetchGithubEndpoint:
    """Test _fetch_github_endpoint function."""

    @patch('ai_model_catalog.fetch_repo._make_github_request')
    def test_fetch_github_endpoint_success(self, mock_request):
        """Test fetching GitHub endpoint successfully."""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 1}, {"id": 2}]
        mock_request.return_value = mock_response
        
        result = _fetch_github_endpoint("https://api.github.com/test")
        assert result == [{"id": 1}, {"id": 2}]

    @patch('ai_model_catalog.fetch_repo._make_github_request')
    def test_fetch_github_endpoint_exception(self, mock_request):
        """Test fetching GitHub endpoint with exception."""
        mock_request.side_effect = GitHubAPIError("API error")
        
        with pytest.raises(GitHubAPIError):
            _fetch_github_endpoint("https://api.github.com/test")


class TestFetchReadmeContent:
    """Test _fetch_readme_content function."""

    @patch('ai_model_catalog.fetch_repo._make_github_request')
    def test_fetch_readme_content_success(self, mock_request):
        """Test fetching README content successfully."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": "IyBUZXN0IFJFQURNRSBGaWxl",  # Base64 encoded "Test README File"
            "encoding": "base64"
        }
        mock_request.return_value = mock_response
        
        result = _fetch_readme_content("test", "repo")
        assert result == "Test README File"

    @patch('ai_model_catalog.fetch_repo._make_github_request')
    def test_fetch_readme_content_not_found(self, mock_request):
        """Test fetching README content when not found."""
        mock_request.side_effect = GitHubAPIError("Not found")
        
        result = _fetch_readme_content("test", "repo")
        assert result == ""

    @patch('ai_model_catalog.fetch_repo._make_github_request')
    def test_fetch_readme_content_invalid_encoding(self, mock_request):
        """Test fetching README content with invalid encoding."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": "Test content",
            "encoding": "invalid"
        }
        mock_request.return_value = mock_response
        
        result = _fetch_readme_content("test", "repo")
        assert result == ""


class TestFetchRepositoryCounts:
    """Test _fetch_repository_counts function."""

    @patch('ai_model_catalog.fetch_repo._get_total_count_from_link_header')
    def test_fetch_repository_counts_success(self, mock_get_count):
        """Test fetching repository counts successfully."""
        mock_get_count.return_value = 5
        
        result = _fetch_repository_counts("test", "repo")
        
        expected = {
            "issues": 5,
            "pull_requests": 5,
            "commits": 5,
            "releases": 5,
        }
        assert result == expected

    @patch('ai_model_catalog.fetch_repo._get_total_count_from_link_header')
    def test_fetch_repository_counts_exception(self, mock_get_count):
        """Test fetching repository counts with exception."""
        mock_get_count.side_effect = GitHubAPIError("API error")
        
        result = _fetch_repository_counts("test", "repo")
        
        expected = {
            "issues": 0,
            "pull_requests": 0,
            "commits": 0,
            "releases": 0,
        }
        assert result == expected


class TestFetchRepositorySamples:
    """Test _fetch_repository_samples function."""

    @patch('ai_model_catalog.fetch_repo._fetch_github_endpoint')
    def test_fetch_repository_samples_success(self, mock_fetch):
        """Test fetching repository samples successfully."""
        mock_fetch.return_value = [{"id": 1}, {"id": 2}]
        
        result = _fetch_repository_samples("test", "repo")
        
        expected = {
            "issues": [{"id": 1}, {"id": 2}],
            "pull_requests": [{"id": 1}, {"id": 2}],
            "commits": [{"id": 1}, {"id": 2}],
            "releases": [{"id": 1}, {"id": 2}],
        }
        assert result == expected

    @patch('ai_model_catalog.fetch_repo._fetch_github_endpoint')
    def test_fetch_repository_samples_exception(self, mock_fetch):
        """Test fetching repository samples with exception."""
        mock_fetch.side_effect = GitHubAPIError("API error")
        
        result = _fetch_repository_samples("test", "repo")
        
        expected = {
            "issues": [],
            "pull_requests": [],
            "commits": [],
            "releases": [],
        }
        assert result == expected


class TestExtractActionsRuns:
    """Test _extract_actions_runs function."""

    def test_extract_actions_runs_success(self):
        """Test extracting actions runs successfully."""
        actions_data = [
            {"workflow_runs": [{"id": 1}, {"id": 2}]},
            {"workflow_runs": [{"id": 3}]},
        ]
        
        result = _extract_actions_runs(actions_data)
        assert result == [{"id": 1}, {"id": 2}, {"id": 3}]

    def test_extract_actions_runs_empty(self):
        """Test extracting actions runs from empty data."""
        actions_data = []
        
        result = _extract_actions_runs(actions_data)
        assert result == []


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
        assert result == 100 * 1024 * 1024


class TestFetchHfReadme:
    """Test _fetch_hf_readme function."""

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_hf_readme_success(self, mock_get):
        """Test fetching HF README successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "# Test README"
        mock_get.return_value = mock_response
        
        result = _fetch_hf_readme("test/model")
        assert result == "# Test README"

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_hf_readme_not_found(self, mock_get):
        """Test fetching HF README when not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = _fetch_hf_readme("test/model")
        assert result == ""

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_hf_readme_exception(self, mock_get):
        """Test fetching HF README with exception."""
        mock_get.side_effect = RequestException("Network error")
        
        result = _fetch_hf_readme("test/model")
        assert result == ""


class TestFetchModelData:
    """Test fetch_model_data function."""

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_model_data_success(self, mock_get):
        """Test fetching model data successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test/model",
            "downloads": 1000,
            "likes": 50,
            "tags": ["nlp", "text"],
            "pipeline_tag": "text-classification",
            "library_name": "transformers",
            "model_index": "pytorch_model.bin",
            "safetensors": [{"size": 1024}],
            "siblings": [{"rfilename": "config.json"}],
            "card_data": {"content": "# Model Card"},
            "last_modified": "2024-01-01T00:00:00.000Z",
        }
        mock_get.return_value = mock_response
        
        result = fetch_model_data("test/model")
        
        assert result["id"] == "test/model"
        assert result["downloads"] == 1000
        assert result["likes"] == 50
        assert result["tags"] == ["nlp", "text"]
        assert result["readme"] == "# Model Card"

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_model_data_not_found(self, mock_get):
        """Test fetching model data when not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(RepositoryDataError, match="Model not found"):
            fetch_model_data("test/model")

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_model_data_exception(self, mock_get):
        """Test fetching model data with exception."""
        mock_get.side_effect = RequestException("Network error")
        
        with pytest.raises(RepositoryDataError, match="Failed to fetch model data"):
            fetch_model_data("test/model")


class TestFetchHfModel:
    """Test fetch_hf_model function."""

    @patch('ai_model_catalog.fetch_repo.fetch_model_data')
    def test_fetch_hf_model_success(self, mock_fetch):
        """Test fetching HF model successfully."""
        mock_fetch.return_value = {"id": "test/model", "downloads": 1000}
        
        result = fetch_hf_model("test/model")
        
        assert result["id"] == "test/model"
        assert result["downloads"] == 1000

    @patch('ai_model_catalog.fetch_repo.fetch_model_data')
    def test_fetch_hf_model_exception(self, mock_fetch):
        """Test fetching HF model with exception."""
        mock_fetch.side_effect = RepositoryDataError("Model error")
        
        with pytest.raises(RepositoryDataError):
            fetch_hf_model("test/model")


class TestFetchDatasetData:
    """Test fetch_dataset_data function."""

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_dataset_data_success(self, mock_get):
        """Test fetching dataset data successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test/dataset",
            "downloads": 500,
            "likes": 25,
            "tags": ["dataset", "nlp"],
            "task_categories": ["text-classification"],
            "author": "test",
            "license": "mit",
            "card_data": {"content": "# Dataset Card"},
            "last_modified": "2024-01-01T00:00:00.000Z",
        }
        mock_get.return_value = mock_response
        
        result = fetch_dataset_data("test/dataset")
        
        assert result["id"] == "test/dataset"
        assert result["downloads"] == 500
        assert result["likes"] == 25
        assert result["tags"] == ["dataset", "nlp"]
        assert result["readme"] == "# Dataset Card"

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_dataset_data_not_found(self, mock_get):
        """Test fetching dataset data when not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(RepositoryDataError, match="Dataset not found"):
            fetch_dataset_data("test/dataset")

    @patch('ai_model_catalog.fetch_repo.requests.get')
    def test_fetch_dataset_data_exception(self, mock_get):
        """Test fetching dataset data with exception."""
        mock_get.side_effect = RequestException("Network error")
        
        with pytest.raises(RepositoryDataError, match="Failed to fetch dataset data"):
            fetch_dataset_data("test/dataset")


class TestFetchRepoData:
    """Test fetch_repo_data function."""

    @patch('ai_model_catalog.fetch_repo._fetch_github_api_data')
    @patch('ai_model_catalog.fetch_repo._format_repo_api_data')
    def test_fetch_repo_data_success(self, mock_format, mock_fetch):
        """Test fetching repo data successfully."""
        mock_fetch.return_value = {"name": "test-repo"}
        mock_format.return_value = {"formatted": "data"}
        
        result = fetch_repo_data("test", "repo")
        
        assert result == {"formatted": "data"}
        mock_fetch.assert_called_once_with("test", "repo")
        mock_format.assert_called_once_with({"name": "test-repo"})

    @patch('ai_model_catalog.fetch_repo._fetch_github_api_data')
    def test_fetch_repo_data_github_error(self, mock_fetch):
        """Test fetching repo data with GitHub API error."""
        mock_fetch.side_effect = GitHubAPIError("API error")
        
        with pytest.raises(GitHubAPIError):
            fetch_repo_data("test", "repo")

    @patch('ai_model_catalog.fetch_repo._fetch_github_api_data')
    def test_fetch_repo_data_repository_error(self, mock_fetch):
        """Test fetching repo data with repository error."""
        mock_fetch.side_effect = RepositoryDataError("Repo error")
        
        with pytest.raises(RepositoryDataError):
            fetch_repo_data("test", "repo")

    @patch('ai_model_catalog.fetch_repo._fetch_github_api_data')
    def test_fetch_repo_data_unexpected_error(self, mock_fetch):
        """Test fetching repo data with unexpected error."""
        mock_fetch.side_effect = ValueError("Unexpected error")
        
        with pytest.raises(RepositoryDataError, match="Unexpected error"):
            fetch_repo_data("test", "repo")


# Import ANY for mock assertions
from unittest.mock import ANY
