"""Enhanced tests for score_ramp_up_time module."""

import os
from unittest.mock import Mock, patch

from ai_model_catalog.metrics.score_ramp_up_time import (
    RampUpMetric,
    LLMRampUpMetric,
    score_ramp_up_time,
)


class TestRampUpMetric:
    """Test RampUpMetric class."""

    def test_score_with_good_readme(self):
        """Test scoring with a good README."""
        metric = RampUpMetric()
        model_data = {"readme": "A" * 300}  # 300 characters
        result = metric.score(model_data)
        assert result == 0.3  # <500 chars bucket

    def test_score_with_short_readme(self):
        """Test scoring with a short README."""
        metric = RampUpMetric()
        model_data = {"readme": "Short"}  # Less than 500 characters
        result = metric.score(model_data)
        assert result == 0.3  # <500 chars bucket

    def test_score_with_empty_readme(self):
        """Test scoring with empty README."""
        metric = RampUpMetric()
        model_data = {"readme": ""}
        result = metric.score(model_data)
        assert result == 0.0

    def test_score_with_none_readme(self):
        """Test scoring with None README."""
        metric = RampUpMetric()
        model_data = {"readme": None}
        result = metric.score(model_data)
        assert result == 0.0

    def test_score_with_missing_readme(self):
        """Test scoring with missing README key."""
        metric = RampUpMetric()
        model_data = {}
        result = metric.score(model_data)
        assert result == 0.0

    def test_score_with_exactly_500_chars(self):
        """Test scoring with exactly 500 characters."""
        metric = RampUpMetric()
        model_data = {"readme": "A" * 500}
        result = metric.score(model_data)
        assert result == 0.6  # 500-1499 chars bucket

    def test_score_with_499_chars(self):
        """Test scoring with 499 characters."""
        metric = RampUpMetric()
        model_data = {"readme": "A" * 499}
        result = metric.score(model_data)
        assert result == 0.3  # <500 chars bucket


class TestLLMRampUpMetric:
    """Test LLMRampUpMetric class."""

    def test_init(self):
        """Test initialization."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            assert metric.llm_service == mock_service

    def test_score_with_llm_success(self):
        """Test score_with_llm with successful LLM analysis."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.analyze_readme_quality.return_value = {
                "installation_quality": 0.8,
                "documentation_completeness": 0.7,
                "example_quality": 0.9,
                "overall_readability": 0.8,
            }
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            data = {"readme": "A comprehensive README with installation instructions"}
            result = metric.score_with_llm(data)

            # Expected: (0.8*0.3 + 0.7*0.25 + 0.9*0.25 + 0.8*0.2) / 1.0
            expected = 0.8 * 0.3 + 0.7 * 0.25 + 0.9 * 0.25 + 0.8 * 0.2
            assert result == expected
            mock_service.analyze_readme_quality.assert_called_once_with(
                "A comprehensive README with installation instructions"
            )

    def test_score_with_llm_empty_readme(self):
        """Test score_with_llm with empty README content."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            data = {"readme": ""}
            result = metric.score_with_llm(data)
            assert result == 0.0
            mock_service.analyze_readme_quality.assert_not_called()

    def test_score_with_llm_whitespace_only_readme(self):
        """Test score_with_llm with whitespace-only README."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            data = {"readme": "   \n\t   "}
            result = metric.score_with_llm(data)
            assert result == 0.0
            mock_service.analyze_readme_quality.assert_not_called()

    def test_score_with_llm_no_analysis(self):
        """Test score_with_llm when LLM returns no analysis."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.analyze_readme_quality.return_value = None
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            data = {"readme": "A comprehensive README"}
            result = metric.score_with_llm(data)
            assert result is None

    def test_score_with_llm_empty_analysis(self):
        """Test score_with_llm when LLM returns empty analysis."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.analyze_readme_quality.return_value = {}
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            data = {"readme": "A comprehensive README"}
            result = metric.score_with_llm(data)
            assert result is None  # Empty analysis returns None

    def test_score_with_llm_partial_analysis(self):
        """Test score_with_llm with partial LLM analysis."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.analyze_readme_quality.return_value = {
                "installation_quality": 0.8,
                "documentation_completeness": 0.7,
                # Missing example_quality and overall_readability
            }
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            data = {"readme": "A comprehensive README"}
            result = metric.score_with_llm(data)

            # Expected: (0.8*0.3 + 0.7*0.25) / (0.3 + 0.25)
            expected = (0.8 * 0.3 + 0.7 * 0.25) / (0.3 + 0.25)
            assert result == expected

    def test_score_without_llm_good_readme(self):
        """Test score_without_llm with good README."""
        metric = LLMRampUpMetric()
        data = {"readme": "A" * 300}
        result = metric.score_without_llm(data)
        assert result == 0.15  # 300/2000 = 0.15

    def test_score_without_llm_short_readme(self):
        """Test score_without_llm with short README."""
        metric = LLMRampUpMetric()
        data = {"readme": "Short"}
        result = metric.score_without_llm(data)
        # Short README (5 chars) / 2000 = 0.0025, rounded to 0.0
        assert result == 0.0

    def test_score_without_llm_empty_readme(self):
        """Test score_without_llm with empty README."""
        metric = LLMRampUpMetric()
        data = {"readme": ""}
        result = metric.score_without_llm(data)
        assert result == 0.0

    def test_score_without_llm_medium_readme(self):
        """Test score_without_llm with medium-length README."""
        metric = LLMRampUpMetric()
        data = {"readme": "A" * 1000}  # 1000 chars
        result = metric.score_without_llm(data)
        assert result == 0.5  # 1000/2000 = 0.5

    def test_score_without_llm_very_long_readme(self):
        """Test score_without_llm with very long README."""
        metric = LLMRampUpMetric()
        data = {"readme": "A" * 2000}  # 2000 chars
        result = metric.score_without_llm(data)
        assert result == 1.0  # Should be capped at 1.0

    def test_score_with_llm_from_description(self):
        """Test score_with_llm when README comes from description field."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.analyze_readme_quality.return_value = {
                "installation_quality": 0.8,
                "documentation_completeness": 0.7,
                "example_quality": 0.9,
                "overall_readability": 0.8,
            }
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            data = {
                "description": "A comprehensive description with installation instructions"
            }
            result = metric.score_with_llm(data)

            expected = 0.8 * 0.3 + 0.7 * 0.25 + 0.9 * 0.25 + 0.8 * 0.2
            assert result == expected
            mock_service.analyze_readme_quality.assert_called_once_with(
                "A comprehensive description with installation instructions"
            )

    def test_score_with_llm_from_carddata(self):
        """Test score_with_llm when README comes from cardData.content field."""
        with patch(
            "ai_model_catalog.metrics.llm_base.get_llm_service"
        ) as mock_get_service:
            mock_service = Mock()
            mock_service.analyze_readme_quality.return_value = {
                "installation_quality": 0.8,
                "documentation_completeness": 0.7,
                "example_quality": 0.9,
                "overall_readability": 0.8,
            }
            mock_get_service.return_value = mock_service

            metric = LLMRampUpMetric()
            data = {
                "readme": "",
                "description": "",
                "cardData": {
                    "content": "A comprehensive card content with installation instructions"
                },
            }
            result = metric.score_with_llm(data)

            expected = 0.8 * 0.3 + 0.7 * 0.25 + 0.9 * 0.25 + 0.8 * 0.2
            assert result == expected
            mock_service.analyze_readme_quality.assert_called_once_with(
                "A comprehensive card content with installation instructions"
            )


class TestScoreRampUpTime:
    """Test score_ramp_up_time function."""

    def test_with_llm_key_available(self):
        """Test when LLM key is available."""
        with patch.dict(os.environ, {"GEN_AI_STUDIO_API_KEY": "test_key"}):
            with patch(
                "ai_model_catalog.metrics.score_ramp_up_time.LLMRampUpMetric"
            ) as mock_llm_metric:
                mock_instance = Mock()
                mock_instance.score.return_value = 0.8
                mock_llm_metric.return_value = mock_instance

                result = score_ramp_up_time("Test README")
                assert result == 0.8
                mock_instance.score.assert_called_once_with({"readme": "Test README"})

    def test_without_llm_key(self):
        """Test when LLM key is not available."""
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "ai_model_catalog.metrics.score_ramp_up_time.RampUpMetric"
            ) as mock_traditional_metric:
                mock_instance = Mock()
                mock_instance.score.return_value = 0.6
                mock_traditional_metric.return_value = mock_instance

                result = score_ramp_up_time("Test README")
                assert result == 0.6
                mock_instance.score.assert_called_once_with({"readme": "Test README"})

    def test_with_empty_llm_key(self):
        """Test when LLM key is empty string."""
        with patch.dict(os.environ, {"GEN_AI_STUDIO_API_KEY": ""}):
            with patch(
                "ai_model_catalog.metrics.score_ramp_up_time.RampUpMetric"
            ) as mock_traditional_metric:
                mock_instance = Mock()
                mock_instance.score.return_value = 0.6
                mock_traditional_metric.return_value = mock_instance

                result = score_ramp_up_time("Test README")
                assert result == 0.6
                mock_instance.score.assert_called_once_with({"readme": "Test README"})

    def test_with_none_llm_key(self):
        """Test when LLM key is None."""
        with patch.dict(os.environ, {"GEN_AI_STUDIO_API_KEY": "None"}):
            # The function checks if the env var exists, not its value
            # So "None" string will still trigger LLM path
            with patch(
                "ai_model_catalog.metrics.score_ramp_up_time.LLMRampUpMetric"
            ) as mock_llm_metric:
                mock_instance = Mock()
                mock_instance.score.return_value = 0.5
                mock_llm_metric.return_value = mock_instance

                result = score_ramp_up_time("Test README")
                assert result == 0.5
                mock_instance.score.assert_called_once_with({"readme": "Test README"})
