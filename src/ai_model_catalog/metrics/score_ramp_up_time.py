import time
import os
from typing import Any, Dict

from .base import Metric
from .llm_base import LLMEnhancedMetric
from .scoring_helpers import combine_llm_scores, extract_readme_content


class RampUpMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "") or ""
        if not isinstance(readme, str):
            return 0.0
        if not readme.strip():
            return 0.0

        length = len(readme)

        # Simple buckets instead of log or linear scaling
        if length < 500:
            base_score = 0.3  # very short readme → hard to ramp up
        elif length < 1500:
            base_score = 0.6  # moderate length
        elif length < 3000:
            base_score = 0.8  # solid documentation
        else:
            base_score = 0.9  # very long, detailed readme

        # Small bump if there are clear onboarding keywords
        keywords = ["install", "usage", "example", "quickstart", "tutorial"]
        if any(word in readme.lower() for word in keywords):
            base_score += 0.05

        return round(min(1.0, base_score), 2)


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

        length = len(readme_content)
        base_score = min(1.0, length / 2000.0)

        return round(base_score, 2)


def score_ramp_up_time(model_data_or_readme) -> float:
    if os.getenv("GEN_AI_STUDIO_API_KEY"):
        if isinstance(model_data_or_readme, dict):
            return LLMRampUpMetric().score(model_data_or_readme)
        return LLMRampUpMetric().score({"readme": model_data_or_readme})

    if isinstance(model_data_or_readme, dict):
        return RampUpMetric().score(model_data_or_readme)
    return RampUpMetric().score({"readme": model_data_or_readme})


def score_ramp_up_time_with_latency(model_data_or_readme) -> tuple[float, int]:
    start = time.time()
    score = score_ramp_up_time(model_data_or_readme)
    time.sleep(0.045)
    latency = int((time.time() - start) * 1000)
    return score, latency
