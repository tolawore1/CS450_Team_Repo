"""Tests for scoring_helpers module."""

from ai_model_catalog.metrics.scoring_helpers import (
    combine_llm_scores,
    extract_readme_content,
    extract_dataset_info,
    validate_llm_response,
)


class TestCombineLLMScores:
    """Test combine_llm_scores function."""

    def test_valid_scores(self):
        """Test with valid scores and weights."""
        llm_analysis = {
            "installation_quality": 0.8,
            "documentation_completeness": 0.6,
            "example_quality": 0.9,
        }
        weights = {
            "installation_quality": 0.3,
            "documentation_completeness": 0.4,
            "example_quality": 0.3,
        }

        result = combine_llm_scores(llm_analysis, weights)
        expected = (0.8 * 0.3 + 0.6 * 0.4 + 0.9 * 0.3) / (0.3 + 0.4 + 0.3)
        assert result == expected

    def test_partial_scores(self):
        """Test with only some keys present."""
        llm_analysis = {
            "installation_quality": 0.8,
            "missing_key": 0.5,
        }
        weights = {
            "installation_quality": 0.5,
            "missing_key": 0.5,
        }

        result = combine_llm_scores(llm_analysis, weights)
        # Only installation_quality is used: (0.8 * 0.5) / 0.5 = 0.8
        # But the function actually uses both keys if they exist in analysis
        # So: (0.8 * 0.5 + 0.5 * 0.5) / (0.5 + 0.5) = 0.65
        assert result == 0.65

    def test_invalid_score_types(self):
        """Test with invalid score types."""
        llm_analysis = {
            "valid_score": 0.8,
            "invalid_score": "not_a_number",
            "another_invalid": None,
        }
        weights = {
            "valid_score": 0.5,
            "invalid_score": 0.3,
            "another_invalid": 0.2,
        }

        result = combine_llm_scores(llm_analysis, weights)
        assert result == 0.8  # Only valid_score is used

    def test_scores_out_of_range(self):
        """Test with scores outside 0-1 range."""
        llm_analysis = {
            "valid_score": 0.8,
            "too_high": 1.5,
            "too_low": -0.2,
        }
        weights = {
            "valid_score": 0.5,
            "too_high": 0.3,
            "too_low": 0.2,
        }

        result = combine_llm_scores(llm_analysis, weights)
        assert result == 0.8  # Only valid_score is used

    def test_zero_total_weight(self):
        """Test when no valid scores are found."""
        llm_analysis = {
            "invalid_score": "not_a_number",
        }
        weights = {
            "invalid_score": 0.5,
        }

        result = combine_llm_scores(llm_analysis, weights)
        assert result == 0.0

    def test_empty_analysis(self):
        """Test with empty analysis dict."""
        llm_analysis = {}
        weights = {"some_key": 0.5}

        result = combine_llm_scores(llm_analysis, weights)
        assert result == 0.0

    def test_empty_weights(self):
        """Test with empty weights dict."""
        llm_analysis = {"score": 0.8}
        weights = {}

        result = combine_llm_scores(llm_analysis, weights)
        assert result == 0.0


class TestExtractReadmeContent:
    """Test extract_readme_content function."""

    def test_readme_field(self):
        """Test extraction from readme field."""
        data = {"readme": "This is a README"}
        result = extract_readme_content(data)
        assert result == "This is a README"

    def test_description_fallback(self):
        """Test fallback to description when readme is empty."""
        data = {"readme": "", "description": "This is a description"}
        result = extract_readme_content(data)
        assert result == "This is a description"

    def test_carddata_fallback(self):
        """Test fallback to cardData.content when readme and description are empty."""
        data = {
            "readme": "",
            "description": "",
            "cardData": {"content": "This is card content"},
        }
        result = extract_readme_content(data)
        assert result == "This is card content"

    def test_none_values(self):
        """Test with None values."""
        data = {"readme": None, "description": None, "cardData": {"content": None}}
        result = extract_readme_content(data)
        assert result == ""

    def test_missing_fields(self):
        """Test with missing fields."""
        data = {}
        result = extract_readme_content(data)
        assert result == ""

    def test_priority_order(self):
        """Test that readme takes priority over description and cardData."""
        data = {
            "readme": "README content",
            "description": "Description content",
            "cardData": {"content": "Card content"},
        }
        result = extract_readme_content(data)
        assert result == "README content"


class TestExtractDatasetInfo:
    """Test extract_dataset_info function."""

    def test_full_data(self):
        """Test with all fields present."""
        data = {
            "description": "A test dataset",
            "tags": ["nlp", "text"],
            "taskCategories": ["text-classification"],
            "downloads": 1000,
            "author": "test_author",
            "license": "MIT",
        }
        result = extract_dataset_info(data)
        assert result == data

    def test_partial_data(self):
        """Test with some fields missing."""
        data = {
            "description": "A test dataset",
            "tags": ["nlp"],
        }
        result = extract_dataset_info(data)
        expected = {
            "description": "A test dataset",
            "tags": ["nlp"],
            "taskCategories": [],
            "downloads": 0,
            "author": "",
            "license": "",
        }
        assert result == expected

    def test_empty_data(self):
        """Test with empty data."""
        data = {}
        result = extract_dataset_info(data)
        expected = {
            "description": "",
            "tags": [],
            "taskCategories": [],
            "downloads": 0,
            "author": "",
            "license": "",
        }
        assert result == expected

    def test_none_values(self):
        """Test with None values."""
        data = {
            "description": None,
            "tags": None,
            "taskCategories": None,
            "downloads": None,
            "author": None,
            "license": None,
        }
        result = extract_dataset_info(data)
        # The function uses .get() with defaults, so None values are preserved
        assert result["description"] is None
        assert result["tags"] is None
        assert result["taskCategories"] is None
        assert result["downloads"] is None
        assert result["author"] is None
        assert result["license"] is None


class TestValidateLLMResponse:
    """Test validate_llm_response function."""

    def test_valid_response(self):
        """Test with valid response structure."""
        response = {
            "score1": 0.8,
            "score2": 0.6,
            "score3": 0.9,
        }
        expected_keys = ["score1", "score2", "score3"]
        result = validate_llm_response(response, expected_keys)
        assert result is True

    def test_invalid_type(self):
        """Test with non-dict response."""
        response = "not a dict"
        expected_keys = ["score1"]
        result = validate_llm_response(response, expected_keys)
        assert result is False

    def test_missing_key(self):
        """Test with missing required key."""
        response = {
            "score1": 0.8,
            "score2": 0.6,
        }
        expected_keys = ["score1", "score2", "missing_key"]
        result = validate_llm_response(response, expected_keys)
        assert result is False

    def test_invalid_score_type(self):
        """Test with non-numeric score."""
        response = {
            "score1": 0.8,
            "score2": "not_a_number",
        }
        expected_keys = ["score1", "score2"]
        result = validate_llm_response(response, expected_keys)
        assert result is False

    def test_score_out_of_range_high(self):
        """Test with score above 1.0."""
        response = {
            "score1": 0.8,
            "score2": 1.5,
        }
        expected_keys = ["score1", "score2"]
        result = validate_llm_response(response, expected_keys)
        assert result is False

    def test_score_out_of_range_low(self):
        """Test with score below 0.0."""
        response = {
            "score1": 0.8,
            "score2": -0.1,
        }
        expected_keys = ["score1", "score2"]
        result = validate_llm_response(response, expected_keys)
        assert result is False

    def test_edge_case_scores(self):
        """Test with edge case scores (0.0 and 1.0)."""
        response = {
            "score1": 0.0,
            "score2": 1.0,
        }
        expected_keys = ["score1", "score2"]
        result = validate_llm_response(response, expected_keys)
        assert result is True

    def test_empty_expected_keys(self):
        """Test with empty expected keys list."""
        response = {"score1": 0.8}
        expected_keys = []
        result = validate_llm_response(response, expected_keys)
        assert result is True

    def test_empty_response(self):
        """Test with empty response dict."""
        response = {}
        expected_keys = ["score1"]
        result = validate_llm_response(response, expected_keys)
        assert result is False
