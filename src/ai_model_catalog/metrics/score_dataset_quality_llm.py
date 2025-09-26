"""LLM-enhanced Dataset Quality metric implementation."""

from typing import Any, Dict

from .constants import DATASET_KEYWORDS, KNOWN_DATASETS
from .llm_base import LLMEnhancedMetric
from .scoring_helpers import combine_llm_scores, extract_dataset_info


class LLMDatasetQualityMetric(LLMEnhancedMetric):
    """LLM-enhanced Dataset Quality metric."""

    def score_with_llm(self, data: Dict[str, Any]) -> float:
        """Score using LLM analysis of dataset information."""
        dataset_info = extract_dataset_info(data)

        if not dataset_info.get("description", "").strip():
            return 0.0

        # Use LLM to analyze dataset quality
        llm_analysis = self.llm_service.analyze_dataset_quality(dataset_info)

        if not llm_analysis:
            return None  # Fall back to traditional method

        # Combine LLM scores with weights for dataset quality
        weights = {
            "documentation_completeness": 0.3,
            "usage_examples": 0.25,
            "metadata_quality": 0.25,
            "data_description": 0.2,
        }

        return combine_llm_scores(llm_analysis, weights)

    def score_without_llm(self, data: Dict[str, Any]) -> float:
        """Score using traditional keyword matching method."""
        readme_content = data.get("readme", "").strip()
        tags = data.get("tags", [])

        if not readme_content:
            return 0.0

        # Traditional keyword-based scoring
        ds_words = DATASET_KEYWORDS
        known = KNOWN_DATASETS

        content_lower = readme_content.lower()
        has_dataset_word = any(word in content_lower for word in ds_words)
        has_known_name = any(name in content_lower for name in known)
        has_data_link = (
            "](" in readme_content or "http" in readme_content
        ) and has_dataset_word

        tag_str = " ".join(tags).lower()
        has_dataset_tag = any(
            word in tag_str for word in ["dataset", "corpus", "benchmark"]
        ) or any(name in tag_str for name in known)

        hits = sum(
            [
                int(has_dataset_word),
                int(has_known_name),
                int(has_data_link),
                int(has_dataset_tag),
            ]
        )

        return max(0.0, min(1.0, hits / 4.0))


def score_dataset_quality_llm(data: Dict[str, Any]) -> float:
    """Score dataset quality using LLM-enhanced analysis."""
    return LLMDatasetQualityMetric().score(data)
