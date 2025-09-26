"""
LLM-enhanced metrics for AI Model Catalog.

This module wraps the README analyzer LLM (or its offline mock) and combines
those signals with simple heuristics to compute trust-related scores.
"""

from __future__ import annotations

from typing import Any, Dict, List
import logging

from .llm_client import get_readme_llm, LLMReadmeAnalysis

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Raw LLM analysis (returned as a plain dict for easy JSON/serialization)
# ---------------------------------------------------------------------------


def analyze_readme_with_llm(readme_content: str) -> Dict[str, Any]:
    """
    Return a JSON-like dict with README quality indicators from LLM (or mock).

    Keys:
      - documentation_quality (0..1)
      - technical_complexity (0..1)
      - dataset_info_present (bool)
      - performance_claims (bool)
      - usage_instructions (bool)
      - code_examples (bool)
    """
    try:
        a: LLMReadmeAnalysis = get_readme_llm().analyze_readme(readme_content or "")
    except Exception as exc:  # defensive: never break callers/tests on LLM errors
        log.error("LLM README analysis failed: %s", exc)
        a = LLMReadmeAnalysis()

    return {
        "documentation_quality": a.documentation_quality,
        "technical_complexity": a.technical_complexity,
        "dataset_info_present": a.dataset_info_present,
        "performance_claims": a.performance_claims,
        "usage_instructions": a.usage_instructions,
        "code_examples": a.code_examples,
    }


# ---------------------------------------------------------------------------
# Enhanced composite scores (bounded to 0..1)
# ---------------------------------------------------------------------------


def enhanced_ramp_up_score(readme: str) -> float:
    """
    Enhanced ramp-up time scoring using LLM analysis.
    Combines a length baseline with LLM signals (usage instructions, examples, doc quality).
    Returns 0..1.
    """
    text = readme or ""
    # Base score from length (full credit around ~1000 chars)
    base_score = min(1.0, len(text) / 1000.0)

    a = analyze_readme_with_llm(text)
    llm_factors = [
        1.0 if a.get("usage_instructions") else 0.0,
        1.0 if a.get("code_examples") else 0.0,
        float(a.get("documentation_quality") or 0.0),
    ]
    enhanced = (base_score + (sum(llm_factors) / len(llm_factors))) / 2.0
    return max(0.0, min(1.0, enhanced))


def enhanced_code_quality_score(readme: str) -> float:
    """
    Enhanced code quality scoring.
    Blends traditional README indicators (tests/CI/formatting/typing)
    with LLM documentation_quality. Returns 0..1.
    """
    text = (readme or "").lower()
    traditional_indicators = [
        "pytest" in text,
        "github actions" in text or "ci" in text,
        "black" in text or "ruff" in text or "flake8" in text,
        "mypy" in text or "pyright" in text,
    ]
    traditional_score = sum(1 for t in traditional_indicators if t) / len(traditional_indicators)

    a = analyze_readme_with_llm(readme or "")
    llm_score = float(a.get("documentation_quality") or 0.0)

    return max(0.0, min(1.0, (traditional_score + llm_score) / 2.0))


def enhanced_dataset_quality_score(readme: str, tags: List[str]) -> float:
    """
    Enhanced dataset quality scoring.
    Combines a simple heuristic (presence of data-related keywords) with the LLM dataset flag.
    Returns 0..1.
    """
    text = (readme or "").lower()
    tag_text = " ".join(tags or []).lower()

    heuristic = any(
        k in text or k in tag_text
        for k in (
            "dataset",
            "data set",
            "cifar",
            "imagenet",
            "squad",
            "dataset card",
            "huggingface dataset",
        )
    )
    traditional = 1.0 if heuristic else 0.0

    a = analyze_readme_with_llm(readme or "")
    llm_dataset = 1.0 if a.get("dataset_info_present") else 0.0

    return max(0.0, min(1.0, (traditional + llm_dataset) / 2.0))


__all__ = [
    "analyze_readme_with_llm",
    "enhanced_ramp_up_score",
    "enhanced_code_quality_score",
    "enhanced_dataset_quality_score",
]
