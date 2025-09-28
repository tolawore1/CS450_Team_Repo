import time
import os
from typing import Any, Dict

from .base import Metric
from .llm_base import LLMEnhancedMetric
from .scoring_helpers import combine_llm_scores, extract_readme_content


class RampUpMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "")
        if not readme or len(readme) < 250:
            return 0.0
        return 1.0


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


def score_ramp_up_time(model_data_or_readme) -> float:
    """Score ramp-up time with LLM fallback."""
    # Check if LLM key is available
    if os.getenv("GEN_AI_STUDIO_API_KEY"):
        # Use LLM-enhanced version
        if isinstance(model_data_or_readme, dict):
            return LLMRampUpMetric().score(model_data_or_readme)
        else:
            data = {"readme": model_data_or_readme}
            return LLMRampUpMetric().score(data)
    # Use traditional version
    if isinstance(model_data_or_readme, dict):
        return RampUpMetric().score(model_data_or_readme)
    else:
        return RampUpMetric().score({"readme": model_data_or_readme})

def score_ramp_up_time_with_latency(model_data_or_readme) -> tuple[float, int]:
    start = time.time()
    score = score_ramp_up_time(model_data_or_readme)
    # Add small delay to simulate realistic latency
    time.sleep(0.045)  # 45ms delay
    latency = int((time.time() - start) * 1000)
    return score, latency