import sys
from pathlib import Path
from unittest.mock import patch

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import after path setup
from ai_model_catalog.cli import (  # pylint: disable=wrong-import-position
    _display_available_owners,
    _display_owner_repositories,
    _extract_license_name,
    _format_count_info,
    _format_model_data,
    _format_repository_data,
)


def test_display_available_owners():
    """Test that _display_available_owners displays the correct owners."""
    with patch("builtins.print") as mock_print:
        _display_available_owners()

        # Check that print was called with the expected owners
        calls = mock_print.call_args_list
        assert any("huggingface" in str(call) for call in calls)
        assert any("openai" in str(call) for call in calls)
        assert any("facebookresearch" in str(call) for call in calls)
        assert any("google-research" in str(call) for call in calls)
        assert any("microsoft" in str(call) for call in calls)


def test_display_owner_repositories_valid_input():
    """Test _display_owner_repositories with valid input (1-5)."""
    with patch("builtins.print") as mock_print:
        _display_owner_repositories(1)  # huggingface

        calls = mock_print.call_args_list
        assert any("huggingface" in str(call) for call in calls)
        assert any("transformers" in str(call) for call in calls)
        assert any("diffusers" in str(call) for call in calls)


def test_display_owner_repositories_invalid_input():
    """Test _display_owner_repositories with invalid input."""
    with patch("builtins.print") as mock_print:
        _display_owner_repositories(6)  # Invalid choice

        calls = mock_print.call_args_list
        assert any("Invalid owner choice" in str(call) for call in calls)
        assert any(
            "Please select a number between 1 and 5" in str(call) for call in calls
        )


def test_display_owner_repositories_edge_cases():
    """Test _display_owner_repositories with edge case inputs."""
    with patch("builtins.print") as mock_print:
        # Test choice 5 (microsoft)
        _display_owner_repositories(5)
        calls = mock_print.call_args_list
        assert any("microsoft" in str(call) for call in calls)
        assert any("DeepSpeed" in str(call) for call in calls)


def test_format_repository_data():
    """Test _format_repository_data function."""
    test_data = {
        "full_name": "test/repo",
        "stargazers_count": 100,
        "forks_count": 50,
        "language": "Python",
        "pushed_at": "2023-01-01",
        "open_issues_count": 10,
        "size": 1000,
        "license": {"spdx_id": "MIT"},
        "description": "Test repo",
        "default_branch": "main",
        "readme": "Test readme content",
    }

    result = _format_repository_data(test_data, "test", "repo")

    assert result["full_name"] == "test/repo"
    assert result["stars"] == 100
    assert result["forks"] == 50
    assert result["language"] == "Python"
    assert result["license_name"] == "MIT"


def test_format_model_data():
    """Test _format_model_data function."""
    test_data = {
        "modelId": "test-model",
        "author": "test-author",
        "description": "Test model",
        "modelSize": 5000000,
        "downloads": 1000,
        "lastModified": "2023-01-01",
        "readme": "Test model readme",
        "license": {"spdx_id": "Apache-2.0"},
        "tags": ["nlp", "transformer"],
        "pipeline_tag": "text-classification",
    }

    result = _format_model_data(test_data, "test-model")

    assert result["model_name"] == "test-model"
    assert result["author"] == "test-author"
    assert result["model_size"] == 5000000
    assert result["license_name"] == "Apache-2.0"
    assert result["tags"] == ["nlp", "transformer"]


def test_extract_license_name_dict():
    """Test _extract_license_name with dictionary input."""
    license_info = {"spdx_id": "MIT"}
    result = _extract_license_name(license_info)
    assert result == "MIT"


def test_extract_license_name_string():
    """Test _extract_license_name with string input."""
    license_info = "Apache-2.0"
    result = _extract_license_name(license_info)
    assert result == "Apache-2.0"


def test_extract_license_name_none():
    """Test _extract_license_name with None input."""
    result = _extract_license_name(None)
    assert result == "None"


def test_format_count_info():
    """Test _format_count_info function."""
    data = {"commits_count": 100, "commits": ["commit1", "commit2"]}
    result = _format_count_info(data, "commits", "commits")
    assert "Total commits: 100" in result

    # Test with zero count
    data_zero = {"commits_count": 0, "commits": ["commit1", "commit2"]}
    result_zero = _format_count_info(data_zero, "commits", "commits")
    assert "Recent commits: 2" in result_zero
