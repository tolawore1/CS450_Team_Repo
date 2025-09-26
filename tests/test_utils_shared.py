"""Shared test utilities for metrics."""


def assert_size_scores_structure(scores, expected_min_score=0.9):
    """Assert that size scores have the expected structure."""
    assert isinstance(scores["size"], dict)
    assert "raspberry_pi" in scores["size"]
    assert "jetson_nano" in scores["size"]
    assert "desktop_pc" in scores["size"]
    assert "aws_server" in scores["size"]
    # Size score should be within expected range
    assert expected_min_score <= scores["size_score"] <= 1.0
