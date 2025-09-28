"""Simple CLI tests for the active commands."""

import json
from unittest.mock import mock_open, patch

from typer.testing import CliRunner

from ai_model_catalog.cli import app

runner = CliRunner()


def test_multiple_urls_command():
    """Test multiple-urls command with NDJSON format."""
    with patch("ai_model_catalog.cli.score_model_from_id") as mock_score:
        mock_score.return_value = {
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
            "size_score": {
                "raspberry_pi": 0.2,
                "jetson_nano": 0.4,
                "desktop_pc": 0.95,
                "aws_server": 1.0,
            },
            "size_score_latency": 50,
            "dataset_and_code_score": 0.9,
            "dataset_and_code_score_latency": 15,
            "dataset_quality": 0.7,
            "dataset_quality_latency": 20,
            "code_quality": 0.6,
            "code_quality_latency": 22,
        }

        # Mock the URL_FILE.txt content
        with patch(
            "builtins.open",
            mock_open(
                read_data=(
                    "https://github.com/google-research/bert, "
                    "https://huggingface.co/datasets/bookcorpus/bookcorpus, "
                    "https://huggingface.co/google-bert/bert-base-uncased\n"
                    ",,https://huggingface.co/parvk11/audience_classifier_model\n"
                    ",,https://huggingface.co/openai/whisper-tiny/tree/main"
                )
            ),
        ):
            result = runner.invoke(app, ["multiple-urls"])
            assert result.exit_code == 0

            # Verify NDJSON output (should have 3 lines)
            lines = result.output.strip().split("\n")
            assert len(lines) == 3

            # Check first line
            output_data = json.loads(lines[0])
            assert "name" in output_data
            assert "category" in output_data
            assert "net_score" in output_data
            assert "net_score_latency" in output_data


def test_multiple_urls_command_error_handling():
    """Test multiple-urls command error handling."""
    # Test with invalid URL_FILE.txt content
    with patch("builtins.open", mock_open(read_data="invalid,url,format")):
        result = runner.invoke(app, ["multiple-urls"])
        # Should still exit successfully even with invalid URLs
        assert result.exit_code == 0


def test_multiple_urls_command_empty_file():
    """Test multiple-urls command with empty file."""
    with patch("builtins.open", mock_open(read_data="")):
        result = runner.invoke(app, ["multiple-urls"])
        # Should exit successfully with no output
        assert result.exit_code == 0
        assert result.output.strip() == ""


def test_multiple_urls_command_file_not_found():
    """Test multiple-urls command when URL_FILE.txt doesn't exist."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = runner.invoke(app, [])
        # Should exit with error code
        assert result.exit_code != 0
