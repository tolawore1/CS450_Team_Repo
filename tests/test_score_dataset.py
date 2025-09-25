"""Tests for dataset scoring functionality."""

from unittest.mock import patch

from ai_model_catalog.score_model import score_dataset_from_id

# import pytest


def test_score_dataset_from_id():
    """Test scoring a dataset with mocked data."""
    with patch("ai_model_catalog.score_model.fetch_dataset_data") as mock_fetch:
        mock_fetch.return_value = {
            "license": "mit",
            "author": "test-author",
            "readme": "# Test Dataset\nThis is a test dataset for NLP tasks.",
            "cardData": {},
            "downloads": 1000,
            "lastModified": "2024-01-01",
            "tags": ["dataset", "nlp", "text-classification"],
            "taskCategories": ["text-classification"],
        }

        scores = score_dataset_from_id("test-dataset")

        # Check that all required scores are present
        assert "NetScore" in scores
        assert "ramp_up_time" in scores
        assert "bus_factor" in scores
        assert "performance_claims" in scores
        assert "license" in scores
        assert "size" in scores
        assert "availability" in scores
        assert "dataset_quality" in scores
        assert "code_quality" in scores

        # Check NetScore is calculated
        assert isinstance(scores["NetScore"], float)
        assert 0.0 <= scores["NetScore"] <= 1.0

        # Check size scores are present
        assert isinstance(scores["size"], dict)
        assert "raspberry_pi" in scores["size"]
        assert "jetson_nano" in scores["size"]
        assert "desktop_pc" in scores["size"]
        assert "aws_server" in scores["size"]


def test_score_dataset_from_id_with_minimal_data():
    """Test scoring a dataset with minimal data."""
    with patch("ai_model_catalog.score_model.fetch_dataset_data") as mock_fetch:
        mock_fetch.return_value = {
            "license": "unknown",
            "author": None,
            "readme": "",
            "cardData": {},
            "downloads": 0,
            "lastModified": "",
            "tags": [],
            "taskCategories": [],
        }

        scores = score_dataset_from_id("minimal-dataset")

        # Should still return valid scores
        assert "NetScore" in scores
        assert isinstance(scores["NetScore"], float)
        assert 0.0 <= scores["NetScore"] <= 1.0
