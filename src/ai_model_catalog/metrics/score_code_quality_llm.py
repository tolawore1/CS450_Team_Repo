"""LLM-enhanced Code Quality metric implementation."""

from typing import Any, Dict

from .constants import CI_CD_KEYWORDS
from .llm_base import LLMEnhancedMetric
from .scoring_helpers import combine_llm_scores, extract_readme_content


class LLMCodeQualityMetric(LLMEnhancedMetric):
    """LLM-enhanced Code Quality metric."""

    def score_with_llm(self, data: Dict[str, Any]) -> float:
        """Score using LLM analysis of README content."""
        readme_content = extract_readme_content(data)

        if not readme_content.strip():
            return 0.0

        # Use LLM to analyze code quality indicators
        llm_analysis = self.llm_service.analyze_code_quality_indicators(readme_content)

        if not llm_analysis:
            return None  # Fall back to traditional method

        # Combine LLM scores with weights for code quality
        weights = {
            "testing_framework": 0.3,
            "ci_cd_mentions": 0.25,
            "linting_tools": 0.25,
            "documentation_quality": 0.1,
            "code_organization": 0.1,
        }

        return combine_llm_scores(llm_analysis, weights)

    def score_without_llm(self, data: Dict[str, Any]) -> float:
        """Score using traditional keyword matching method."""
        readme_content = extract_readme_content(data)

        if not readme_content.strip():
            return 0.0

        # Traditional keyword-based scoring
        content_lower = readme_content.lower()

        has_tests = any(
            word in content_lower
            for word in [
                "pytest",
                "unittest",
                "unit test",
                "integration test",
                "tests/",
            ]
        )
        has_ci = any(word in content_lower for word in CI_CD_KEYWORDS)
        has_lint = any(
            word in content_lower
            for word in ["pylint", "flake8", "ruff", "black", "isort", "pre-commit"]
        )
        typing_or_docs = any(
            word in content_lower for word in ["mypy", "type hints", "typed"]
        ) or any(
            word in content_lower
            for word in ["docs/", "documentation", "readthedocs", "api reference"]
        )

        hits = sum([has_tests, has_ci, has_lint, typing_or_docs])
        return max(0.0, min(1.0, hits / 4.0))


def score_code_quality_llm(data: Dict[str, Any]) -> float:
    """Score code quality using LLM-enhanced analysis."""
    return LLMCodeQualityMetric().score(data)
