"""Helper functions for LLM-enhanced scoring."""

from typing import Any, Dict


def combine_llm_scores(
    llm_analysis: Dict[str, Any], weights: Dict[str, float]
) -> float:
    """Combine LLM analysis scores with weights."""
    total_score = 0.0
    total_weight = 0.0

    for key, weight in weights.items():
        if key in llm_analysis and isinstance(llm_analysis[key], (int, float)):
            score = float(llm_analysis[key])
            if 0.0 <= score <= 1.0:  # Validate score range
                total_score += score * weight
                total_weight += weight

    if total_weight == 0:
        return 0.0

    return total_score / total_weight


def extract_readme_content(data: Dict[str, Any]) -> str:
    """Extract README content from data."""
    readme = data.get("readme", "")
    if not readme:
        readme = data.get("description", "")
    if not readme:
        readme = data.get("cardData", {}).get("content", "")

    return readme or ""


def extract_dataset_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract dataset-specific information."""
    return {
        "description": data.get("description", ""),
        "tags": data.get("tags", []),
        "taskCategories": data.get("taskCategories", []),
        "downloads": data.get("downloads", 0),
        "author": data.get("author", ""),
        "license": data.get("license", ""),
    }


def validate_llm_response(response: Dict[str, Any], expected_keys: list) -> bool:
    """Validate that LLM response has expected structure."""
    if not isinstance(response, dict):
        return False

    for key in expected_keys:
        if key not in response:
            return False
        if not isinstance(response[key], (int, float)):
            return False
        if not 0.0 <= float(response[key]) <= 1.0:
            return False

    return True


def calculate_maturity_factor(
    readme: str, author: str, model_size: int, downloads: int
) -> float:
    """Calculate maturity factor based on common patterns."""
    maturity_factor = 1.0

    # Organization reputation boost
    prestigious_orgs = [
        "google",
        "openai",
        "microsoft",
        "facebook",
        "meta",
        "huggingface",
        "nvidia",
        "anthropic",
    ]
    if any(org in author for org in prestigious_orgs):
        maturity_factor *= 1.2

    # Model size indicates complexity
    if model_size > 1000000000:  # >1GB
        maturity_factor *= 1.0  # Large models need good docs
    elif model_size < 10000000:  # <10MB
        maturity_factor *= 0.9  # Small models can have simpler docs

    # Download-based maturity tiers
    download_multipliers = [
        (10000000, 1.0),
        (1000000, 0.95),
        (100000, 0.90),
        (10000, 0.85),
        (1000, 0.80),
        (0, 0.75),
    ]
    for threshold, multiplier in download_multipliers:
        if downloads > threshold:
            maturity_factor *= multiplier
            break

    # Check for experimental indicators
    experimental_keywords = [
        "experimental",
        "beta",
        "alpha",
        "preview",
        "demo",
        "toy",
        "simple",
        "test",
    ]
    if any(keyword in readme for keyword in experimental_keywords):
        if not any(org in author for org in prestigious_orgs):
            maturity_factor *= 0.001  # Significantly reduce for experimental models

    # Check for established indicators
    established_keywords = [
        "production",
        "stable",
        "release",
        "v1",
        "v2",
        "enterprise",
        "bert",
        "transformer",
        "gpt",
    ]
    if any(keyword in readme for keyword in established_keywords):
        maturity_factor *= 1.3  # Boost for established models

    # Check for academic indicators
    academic_keywords = ["paper", "research", "arxiv", "conference", "journal", "study"]
    if any(keyword in readme for keyword in academic_keywords):
        maturity_factor *= 1.1  # Slight boost for research models

    return maturity_factor
