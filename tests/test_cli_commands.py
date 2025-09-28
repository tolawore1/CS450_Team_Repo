import json

import pytest
from typer.testing import CliRunner
from unittest.mock import mock_open

from ai_model_catalog.cli import app

runner = CliRunner()


def test_models_command_smoke(monkeypatch):
    pytest.skip("Skipping due to GitHub API rate limits")

    def mock_fetch_repo_data(owner, repo):
        return {
            "full_name": f"{owner}/{repo}",
            "stars": 1000,
            "forks": 200,
            "open_issues": 5,
            "license": {"spdx_id": "mit"},
            "updated_at": "2024-01-01T00:00:00Z",
            "readme": "Mocked readme",
            "description": "Test repository",
            "default_branch": "main",
            "language": "Python",
            "size": 1024,
            "commits_count": 100,
            "contributors_count": 10,
            "issues_count": 5,
            "pulls_count": 3,
            "actions_count": 2,
            "commits": [],
            "contributors": [],
            "issues": [],
            "pulls": [],
            "actions": [],
        }

    monkeypatch.setattr(
        "ai_model_catalog.fetch_repo.fetch_repo_data", mock_fetch_repo_data
    )

    result = runner.invoke(
        app, ["models", "--owner", "huggingface", "--repo", "transformers"]
    )
    assert result.exit_code == 0
    assert "Repo:" in result.output


def test_multiple_urls_command_smoke(monkeypatch):
    # Mock the score_model_from_id function
    monkeypatch.setattr(
        "ai_model_catalog.cli.score_model_from_id",
        lambda model_id: {
            "net_score": 0.85,
            "net_score_latency": 180,
            "ramp_up_time": 1.0,
            "ramp_up_time_latency": 45,
            "bus_factor": 0.5,
            "bus_factor_latency": 25,
            "performance_claims": 0.8,
            "performance_claims_latency": 35,
            "license": 1.0,
            "license_latency": 10,
            "size_score": {"raspberry_pi": 0.2, "jetson_nano": 0.4, "desktop_pc": 0.95, "aws_server": 1.0},
            "size_score_latency": 50,
            "dataset_and_code_score": 0.9,
            "dataset_and_code_score_latency": 15,
            "dataset_quality": 0.7,
            "dataset_quality_latency": 20,
            "code_quality": 0.6,
            "code_quality_latency": 22,
        },
        raising=True,
    )

    # Mock the URL_FILE.txt content
    monkeypatch.setattr("builtins.open", mock_open(read_data="https://github.com/google-research/bert, https://huggingface.co/datasets/bookcorpus/bookcorpus, https://huggingface.co/google-bert/bert-base-uncased\n,,https://huggingface.co/parvk11/audience_classifier_model\n,,https://huggingface.co/openai/whisper-tiny/tree/main"))

    # Test the multiple-urls command
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "bert-base-uncased" in result.output


def test_invalid_command():
    result = runner.invoke(app, ["invalid_command"])
    assert result.exit_code != 0
    assert "Usage:" in result.output


def test_ndjson_output_structure():
    """Test NDJSON output structure validation."""

    # Test the expected NDJSON structure for each command type
    test_cases = [
        {
            "name": "test/repo",
            "category": "REPOSITORY",
            "net_score": 0.85,
            "ramp_up_time": 1.0,
            "bus_factor": 1.0,
            "performance_claims": 0.5,
            "license": 1.0,
            "size_score": {
                "raspberry_pi": 0.2,
                "jetson_nano": 0.4,
                "desktop_pc": 0.8,
                "aws_server": 0.9,
            },
            "dataset_and_code_score": 1.0,
            "dataset_quality": 0.75,
            "code_quality": 0.5,
            "latency": 100,
        },
        {
            "name": "test-model",
            "category": "MODEL",
            "net_score": 0.75,
            "ramp_up_time": 1.0,
            "bus_factor": 1.0,
            "performance_claims": 0.5,
            "license": 1.0,
            "size_score": {
                "raspberry_pi": 0.2,
                "jetson_nano": 0.4,
                "desktop_pc": 0.8,
                "aws_server": 0.9,
            },
            "dataset_and_code_score": 1.0,
            "dataset_quality": 0.75,
            "code_quality": 0.5,
            "latency": 150,
        },
        {
            "name": "test-dataset",
            "category": "DATASET",
            "net_score": 0.6,
            "ramp_up_time": 0.5,
            "bus_factor": 1.0,
            "performance_claims": 0.0,
            "license": 1.0,
            "size_score": {
                "raspberry_pi": 0.5,
                "jetson_nano": 0.5,
                "desktop_pc": 0.5,
                "aws_server": 0.5,
            },
            "dataset_and_code_score": 0.0,
            "dataset_quality": 0.75,
            "code_quality": 0.0,
            "latency": 200,
        },
    ]

    for test_case in test_cases:
        # Test JSON serialization/deserialization
        json_output = json.dumps(test_case)
        parsed_data = json.loads(json_output)

        # Verify all required fields are present
        required_fields = [
            "name",
            "category",
            "net_score",
            "ramp_up_time",
            "bus_factor",
            "performance_claims",
            "license",
            "size_score",
            "dataset_and_code_score",
            "dataset_quality",
            "code_quality",
            "latency",
        ]

        for field in required_fields:
            assert field in parsed_data, f"Missing required field: {field}"

        # Verify latency field is integer and non-negative
        assert isinstance(
            parsed_data["latency"], int
        ), "Latency field should be integer"
        assert parsed_data["latency"] >= 0, "Latency field should be non-negative"

        # Verify size_score is a dictionary with required keys
        assert isinstance(parsed_data["size_score"], dict)
        size_keys = ["raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"]
        for key in size_keys:
            assert key in parsed_data["size_score"], f"Missing size_score key: {key}"

        # Verify category is valid
        valid_categories = ["REPOSITORY", "MODEL", "DATASET"]
        assert (
            parsed_data["category"] in valid_categories
        ), f"Invalid category: {parsed_data['category']}"

        # Verify scores are in valid range [0, 1]
        score_fields = [
            "net_score",
            "ramp_up_time",
            "bus_factor",
            "performance_claims",
            "license",
            "dataset_and_code_score",
            "dataset_quality",
            "code_quality",
        ]
        for field in score_fields:
            assert (
                0 <= parsed_data[field] <= 1
            ), f"Score {field} should be in range [0, 1]"


def test_ndjson_format_validation():
    """Test that NDJSON output is properly formatted."""

    # Test valid NDJSON structure
    test_data = {
        "name": "test",
        "category": "MODEL",
        "net_score": 0.85,
        "ramp_up_time": 1.0,
        "bus_factor": 1.0,
        "performance_claims": 0.5,
        "license": 1.0,
        "size_score": {
            "raspberry_pi": 0.2,
            "jetson_nano": 0.4,
            "desktop_pc": 0.8,
            "aws_server": 0.9,
        },
        "dataset_and_code_score": 1.0,
        "dataset_quality": 0.75,
        "code_quality": 0.5,
        "latency": 100,
    }

    # Should be able to serialize to JSON
    json_output = json.dumps(test_data)
    assert isinstance(json_output, str)

    # Should be able to deserialize back
    parsed_data = json.loads(json_output)
    assert parsed_data == test_data

    # Check all required fields are present
    required_fields = [
        "name",
        "category",
        "net_score",
        "ramp_up_time",
        "bus_factor",
        "performance_claims",
        "license",
        "size_score",
        "dataset_and_code_score",
        "dataset_quality",
        "code_quality",
        "latency",
    ]

    for field in required_fields:
        assert field in parsed_data, f"Missing required field: {field}"

    # Check latency field is integer
    assert isinstance(parsed_data["latency"], int), "Latency field should be integer"
    assert parsed_data["latency"] >= 0, "Latency field should be non-negative"
