"""Simple CLI tests to boost coverage."""

import json
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from ai_model_catalog.cli import app

runner = CliRunner()


def test_models_command_ndjson_format():
    """Test models command with NDJSON format."""
    with patch("ai_model_catalog.cli.score_repo_from_owner_and_repo") as mock_score:
        mock_score.return_value = {
            "NetScore": 0.85,
            "ramp_up_time": 1.0,
            "bus_factor": 0.5,
            "performance_claims": 0.8,
            "license": 1.0,
            "size": {"raspberry_pi": 0.2},
            "availability": 0.9,
            "dataset_quality": 0.7,
            "code_quality": 0.6,
        }

        with patch("ai_model_catalog.cli.RepositoryHandler") as mock_handler_class:
            mock_handler = MagicMock()
            mock_handler_class.return_value = mock_handler
            mock_handler.fetch_data.return_value = {
                "full_name": "test/repo",
                "stars": 100,
            }

            result = runner.invoke(app, ["models", "--format", "ndjson"])
            assert result.exit_code == 0

            # Verify NDJSON output
            output_data = json.loads(result.output)
            assert "name" in output_data
            assert "category" in output_data
            assert "net_score" in output_data
            assert "latency" in output_data


def test_hf_model_command_ndjson_format():
    """Test hf-model command with NDJSON format."""
    with patch("ai_model_catalog.cli.score_model_from_id") as mock_score:
        mock_score.return_value = {
            "NetScore": 0.75,
            "ramp_up_time": 0.8,
            "bus_factor": 0.6,
            "performance_claims": 0.7,
            "license": 1.0,
            "size": {"raspberry_pi": 0.3},
            "availability": 0.8,
            "dataset_quality": 0.6,
            "code_quality": 0.7,
        }

        with patch("ai_model_catalog.cli.ModelHandler") as mock_handler_class:
            mock_handler = MagicMock()
            mock_handler_class.return_value = mock_handler
            mock_handler.fetch_data.return_value = {
                "modelSize": 123,
                "license": "mit",
            }

            result = runner.invoke(app, ["hf-model", "--format", "ndjson"])
            assert result.exit_code == 0

            # Verify NDJSON output
            output_data = json.loads(result.output)
            assert "name" in output_data
            assert "category" in output_data
            assert "net_score" in output_data
            assert "latency" in output_data


def test_hf_dataset_command_ndjson_format():
    """Test hf-dataset command with NDJSON format."""
    with patch("ai_model_catalog.cli.score_dataset_from_id") as mock_score:
        mock_score.return_value = {
            "NetScore": 0.7,
            "ramp_up_time": 0.6,
            "bus_factor": 0.5,
            "performance_claims": 0.6,
            "license": 1.0,
            "size": {"raspberry_pi": 0.4},
            "availability": 0.7,
            "dataset_quality": 0.8,
            "code_quality": 0.0,
        }

        with patch("ai_model_catalog.cli.fetch_dataset_data") as mock_fetch:
            mock_fetch.return_value = {
                "author": "test",
                "license": "mit",
                "downloads": 1000,
            }

            result = runner.invoke(app, ["hf-dataset", "--format", "ndjson"])
            assert result.exit_code == 0

            # Verify NDJSON output
            output_data = json.loads(result.output)
            assert "name" in output_data
            assert "category" in output_data
            assert "net_score" in output_data
            assert "latency" in output_data


def test_hf_dataset_command_with_tags():
    """Test hf-dataset command with tags and task categories."""
    with patch("ai_model_catalog.cli.fetch_dataset_data") as mock_fetch:
        mock_fetch.return_value = {
            "author": "test",
            "license": "mit",
            "downloads": 1000,
            "lastModified": "2024-01-01",
            "tags": ["nlp", "text", "classification"],
            "taskCategories": ["text-classification", "sentiment-analysis"],
        }

        result = runner.invoke(app, ["hf-dataset", "--dataset-id", "test-dataset"])
        assert result.exit_code == 0
        assert "Tags: nlp, text, classification" in result.output
        assert (
            "Task Categories: text-classification, sentiment-analysis" in result.output
        )


def test_hf_dataset_command_no_tags():
    """Test hf-dataset command without tags."""
    with patch("ai_model_catalog.cli.fetch_dataset_data") as mock_fetch:
        mock_fetch.return_value = {
            "author": "test",
            "license": "mit",
            "downloads": 1000,
            "lastModified": "2024-01-01",
            "tags": [],
            "taskCategories": [],
        }

        result = runner.invoke(app, ["hf-dataset", "--dataset-id", "test-dataset"])
        assert result.exit_code == 0
        assert "Tags:" not in result.output
        assert "Task Categories:" not in result.output


def test_interactive_command():
    """Test interactive command."""
    with patch("ai_model_catalog.cli.interactive_main") as mock_interactive:
        mock_interactive.return_value = None

        result = runner.invoke(app, ["interactive"])
        assert result.exit_code == 0
        mock_interactive.assert_called_once()
