"""Additional tests for scoring_helpers.py to improve coverage."""

from ai_model_catalog.metrics.scoring_helpers import (
    combine_llm_scores,
    extract_readme_content,
    extract_dataset_info,
    validate_llm_response,
    calculate_maturity_factor,
)


class TestScoringHelpersCoverage:
    """Test cases to improve coverage for scoring_helpers.py."""

    def test_combine_llm_scores_empty_analysis(self):
        """Test combine_llm_scores with empty analysis."""
        weights = {"test": 0.5}
        result = combine_llm_scores({}, weights)
        assert result == 0.0

    def test_combine_llm_scores_invalid_scores(self):
        """Test combine_llm_scores with invalid scores."""
        llm_analysis = {
            "test1": 1.5,  # Out of range
            "test2": -0.5,  # Out of range
            "test3": "invalid",  # Not a number
        }
        weights = {"test1": 0.3, "test2": 0.3, "test3": 0.4}
        result = combine_llm_scores(llm_analysis, weights)
        assert result == 0.0

    def test_combine_llm_scores_mixed_valid_invalid(self):
        """Test combine_llm_scores with mixed valid and invalid scores."""
        llm_analysis = {
            "test1": 0.8,  # Valid
            "test2": 1.5,  # Invalid - out of range
            "test3": 0.6,  # Valid
        }
        weights = {"test1": 0.3, "test2": 0.3, "test3": 0.4}
        result = combine_llm_scores(llm_analysis, weights)
        # Should only use test1 and test3: (0.8*0.3 + 0.6*0.4) / (0.3 + 0.4) = 0.6857
        assert abs(result - 0.6857) < 0.001

    def test_extract_readme_content_from_description(self):
        """Test extract_readme_content from description field."""
        data = {"description": "Test description"}
        result = extract_readme_content(data)
        assert result == "Test description"

    def test_extract_readme_content_from_card_data(self):
        """Test extract_readme_content from cardData field."""
        data = {"cardData": {"content": "Test content"}}
        result = extract_readme_content(data)
        assert result == "Test content"

    def test_extract_readme_content_empty(self):
        """Test extract_readme_content with empty data."""
        data = {}
        result = extract_readme_content(data)
        assert result == ""

    def test_extract_dataset_info_complete(self):
        """Test extract_dataset_info with complete data."""
        data = {
            "description": "Test dataset",
            "tags": ["nlp", "text"],
            "taskCategories": ["text-classification"],
            "downloads": 1000,
            "author": "test-author",
            "license": "MIT",
        }
        result = extract_dataset_info(data)
        expected = {
            "description": "Test dataset",
            "tags": ["nlp", "text"],
            "taskCategories": ["text-classification"],
            "downloads": 1000,
            "author": "test-author",
            "license": "MIT",
        }
        assert result == expected

    def test_validate_llm_response_invalid_type(self):
        """Test validate_llm_response with invalid type."""
        result = validate_llm_response("not a dict", ["test"])
        assert result is False

    def test_validate_llm_response_missing_key(self):
        """Test validate_llm_response with missing key."""
        response = {"test1": 0.5}
        result = validate_llm_response(response, ["test1", "test2"])
        assert result is False

    def test_validate_llm_response_invalid_value_type(self):
        """Test validate_llm_response with invalid value type."""
        response = {"test1": "not a number"}
        result = validate_llm_response(response, ["test1"])
        assert result is False

    def test_validate_llm_response_out_of_range(self):
        """Test validate_llm_response with out of range values."""
        response = {"test1": 1.5}  # Out of range
        result = validate_llm_response(response, ["test1"])
        assert result is False

    def test_validate_llm_response_valid(self):
        """Test validate_llm_response with valid response."""
        response = {"test1": 0.5, "test2": 0.8}
        result = validate_llm_response(response, ["test1", "test2"])
        assert result is True

    def test_calculate_maturity_factor_prestigious_org(self):
        """Test calculate_maturity_factor with prestigious organization."""
        result = calculate_maturity_factor(
            "Test readme", "google-research", 1000000, 1000
        )
        assert result > 0.5  # Should be boosted

    def test_calculate_maturity_factor_large_model(self):
        """Test calculate_maturity_factor with large model."""
        result = calculate_maturity_factor(
            "Test readme", "test-author", 2000000000, 1000
        )
        assert result > 0.5  # Should be reasonable

    def test_calculate_maturity_factor_small_model(self):
        """Test calculate_maturity_factor with small model."""
        result = calculate_maturity_factor("Test readme", "test-author", 5000000, 1000)
        assert result > 0.5  # Should be reasonable

    def test_calculate_maturity_factor_high_downloads(self):
        """Test calculate_maturity_factor with high downloads."""
        result = calculate_maturity_factor(
            "Test readme", "test-author", 1000000, 15000000
        )
        assert result > 0.5  # Should be reasonable

    def test_calculate_maturity_factor_medium_downloads(self):
        """Test calculate_maturity_factor with medium downloads."""
        result = calculate_maturity_factor(
            "Test readme", "test-author", 1000000, 5000000
        )
        assert result > 0.5  # Should be reasonable

    def test_calculate_maturity_factor_low_downloads(self):
        """Test calculate_maturity_factor with low downloads."""
        result = calculate_maturity_factor("Test readme", "test-author", 1000000, 50000)
        assert result > 0.5  # Should be reasonable

    def test_calculate_maturity_factor_very_low_downloads(self):
        """Test calculate_maturity_factor with very low downloads."""
        result = calculate_maturity_factor("Test readme", "test-author", 1000000, 5000)
        assert result > 0.5  # Should be reasonable

    def test_calculate_maturity_factor_minimal_downloads(self):
        """Test calculate_maturity_factor with minimal downloads."""
        result = calculate_maturity_factor("Test readme", "test-author", 1000000, 500)
        assert result > 0.5  # Should be reasonable

    def test_calculate_maturity_factor_experimental_keywords(self):
        """Test calculate_maturity_factor with experimental keywords."""
        readme = "This is an experimental model for testing"
        result = calculate_maturity_factor(readme, "test-author", 1000000, 1000)
        assert result < 0.1  # Should be significantly reduced

    def test_calculate_maturity_factor_experimental_prestigious(self):
        """Test calculate_maturity_factor with experimental keywords but prestigious org."""
        readme = "This is an experimental model for testing"
        result = calculate_maturity_factor(readme, "google-research", 1000000, 1000)
        assert result > 0.5  # Prestigious org should still get boost

    def test_calculate_maturity_factor_established_keywords(self):
        """Test calculate_maturity_factor with established keywords."""
        readme = "This is a production-ready BERT model"
        result = calculate_maturity_factor(readme, "test-author", 1000000, 1000)
        assert result > 0.5  # Should be boosted

    def test_calculate_maturity_factor_academic_keywords(self):
        """Test calculate_maturity_factor with academic keywords."""
        readme = "This model is described in our research paper"
        result = calculate_maturity_factor(readme, "test-author", 1000000, 1000)
        assert result > 0.5  # Should be slightly boosted

    def test_calculate_maturity_factor_combined_factors(self):
        """Test calculate_maturity_factor with multiple factors."""
        readme = "This is a production BERT model described in our research paper"
        result = calculate_maturity_factor(
            readme, "google-research", 2000000000, 15000000
        )
        # Should have multiple boosts: prestigious org, large model, high downloads,
        # established keywords, academic keywords
        assert result > 1.5  # Should be significantly boosted
