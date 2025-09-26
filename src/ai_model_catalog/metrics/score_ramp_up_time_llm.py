"""LLM-enhanced Ramp-up Time metric implementation."""

from typing import Any, Dict

from .llm_base import LLMEnhancedMetric
from .scoring_helpers import combine_llm_scores, extract_readme_content


class LLMRampUpMetric(LLMEnhancedMetric):
    """LLM-enhanced Ramp-up Time metric."""

    def score_with_llm(self, data: Dict[str, Any]) -> float:
        """Score using LLM analysis of README content."""
        readme_content = extract_readme_content(data)

        if not readme_content.strip():
            return 0.0

        # Use LLM to analyze README quality
        llm_analysis = self.llm_service.analyze_readme_quality(readme_content)

        if not llm_analysis:
            return None  # Fall back to traditional method

        # Combine LLM scores with weights for ramp-up time
        weights = {
            "installation_quality": 0.3,
            "documentation_completeness": 0.25,
            "example_quality": 0.25,
            "overall_readability": 0.2,
        }

        return combine_llm_scores(llm_analysis, weights)

    def score_without_llm(self, data: Dict[str, Any]) -> float:
        """Score using traditional README length method."""
        readme_content = extract_readme_content(data)

        if not readme_content.strip():
            return 0.0

        # Traditional method: README length-based scoring
        length = len(readme_content)
        return min(1.0, length / 250.0)


def score_ramp_up_time_llm(data: Dict[str, Any]) -> float:
    """Score ramp-up time using LLM-enhanced analysis."""
    return LLMRampUpMetric().score(data)
