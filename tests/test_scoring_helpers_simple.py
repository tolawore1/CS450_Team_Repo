"""Simple tests for scoring_helpers.py"""

import pytest
from ai_model_catalog.metrics.scoring_helpers import (
    combine_llm_scores,
    extract_readme_content,
    extract_dataset_info,
    validate_llm_response,
)


def test_combine_llm_scores_valid():
    """Test combining valid LLM scores."""
    llm_analysis = {
        "installation_quality": 0.8,
        "documentation_completeness": 0.6,
    }
    weights = {
        "installation_quality": 0.5,
        "documentation_completeness": 0.5,
    }
    
    result = combine_llm_scores(llm_analysis, weights)
    assert result == 0.7


def test_combine_llm_scores_empty():
    """Test combining scores with empty weights."""
    llm_analysis = {"installation_quality": 0.8}
    weights = {}
    
    result = combine_llm_scores(llm_analysis, weights)
    assert result == 0.00


def test_extract_readme_content_from_readme():
    """Test extracting README from 'readme' field."""
    data = {"readme": "This is a README"}
    result = extract_readme_content(data)
    assert result == "This is a README"


def test_extract_readme_content_from_description():
    """Test extracting README from 'description' field."""
    data = {"readme": "", "description": "This is a description"}
    result = extract_readme_content(data)
    assert result == "This is a description"


def test_extract_readme_content_empty():
    """Test extracting README when no content is available."""
    data = {}
    result = extract_readme_content(data)
    assert result == ""


def test_extract_dataset_info():
    """Test extracting dataset info."""
    data = {
        "description": "A test dataset",
        "tags": ["nlp"],
        "downloads": 1000,
    }
    result = extract_dataset_info(data)
    assert result["description"] == "A test dataset"
    assert result["tags"] == ["nlp"]
    assert result["downloads"] == 1000


def test_validate_llm_response_valid():
    """Test validating a valid LLM response."""
    response = {
        "installation_quality": 0.8,
        "documentation_completeness": 0.6,
    }
    expected_keys = ["installation_quality", "documentation_completeness"]
    
    result = validate_llm_response(response, expected_keys)
    assert result is True


def test_validate_llm_response_invalid():
    """Test validating an invalid LLM response."""
    response = {"installation_quality": 1.5}  # Invalid: > 1.0
    expected_keys = ["installation_quality"]
    
    result = validate_llm_response(response, expected_keys)
    assert result is False
