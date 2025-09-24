"""Tests for the main module entry point."""

# from unittest.mock import MagicMock, patch

# import pytest

from ai_model_catalog.__main__ import main


def test_main_function():
    """Test that main function calls configure_logging and app."""
    with (
        patch("ai_model_catalog.__main__.configure_logging") as mock_logging,
        patch("ai_model_catalog.__main__.app") as mock_app,
    ):

        main()

        # Verify configure_logging was called
        mock_logging.assert_called_once()

        # Verify app was called
        mock_app.assert_called_once()


def test_main_module_execution():
    """Test that the module can be executed directly."""
    with (
        patch("ai_model_catalog.__main__.configure_logging") as mock_logging,
        patch("ai_model_catalog.__main__.app") as mock_app,
    ):

        # Simulate running the module directly
        import ai_model_catalog.__main__

        ai_model_catalog.__main__.main()

        # Verify configure_logging was called
        mock_logging.assert_called_once()

        # Verify app was called
        mock_app.assert_called_once()


def test_main_function_return_type():
    """Test that main function returns None."""
    with (
        patch("ai_model_catalog.__main__.configure_logging"),
        patch("ai_model_catalog.__main__.app"),
    ):

        result = main()
        assert result is None
