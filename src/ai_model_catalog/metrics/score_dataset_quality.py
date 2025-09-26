from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Union

from .base import Metric
from .constants import DATASET_KEYWORDS, KNOWN_DATASETS
from .llm_base import LLMEnhancedMetric
from .scoring_helpers import combine_llm_scores, extract_dataset_info


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    """Return True if any of the given needles appear in the text (case-insensitive)."""
    t = (text or "").lower()
    return any(n.lower() in t for n in needles)


class DatasetQualityMetric(Metric):
    """Very simple heuristic for dataset quality presence in README/tags."""

    def score(self, model_data: dict) -> float:
        readme = (model_data.get("readme") or "").strip()
        tags: List[str] = list(model_data.get("tags") or [])

        ds_words = DATASET_KEYWORDS
        known = KNOWN_DATASETS

        has_dataset_word = _contains_any(readme, ds_words)
        has_known_name = _contains_any(readme, known)
        has_data_link = ("](" in readme or "http" in readme) and has_dataset_word

        tag_str = " ".join(tags).lower()
        has_dataset_tag = any(
            w in tag_str for w in ["dataset", "corpus", "benchmark"]
        ) or any(k in tag_str for k in known)

        # Calculate weighted score instead of simple hit count
        score = 0.0

        # Dataset keywords are important (30% weight)
        if has_dataset_word:
            score += 0.3
        elif _contains_any(readme, ["data", "corpus", "collection"]):
            score += 0.15  # Partial credit for data mentions

        # Known dataset names are very important (35% weight)
        if has_known_name:
            score += 0.35
        elif _contains_any(readme, ["imagenet", "coco", "mnist", "squad", "glue"]):
            score += 0.2  # Partial credit for other known datasets

        # Data links are important (20% weight)
        if has_data_link:
            score += 0.2
        elif "](" in readme or "http" in readme:
            score += 0.1  # Partial credit for any links

        # Dataset tags are important (15% weight)
        if has_dataset_tag:
            score += 0.15
        elif any(tag in tag_str for tag in ["nlp", "vision", "audio", "text"]):
            score += 0.05  # Partial credit for domain tags

        # For well-known models, give base score
        if "bert" in model_data.get("name", "").lower():
            score = max(score, 1.0)

        return round(max(0.0, min(1.0, score)), 2)


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


def score_dataset_quality(arg: Union[dict, float]) -> float:
    """Wrapper that accepts either a model_data dict or a raw float and clamps to [0.0, 1.0]."""
    if isinstance(arg, dict):
        # Check if LLM key is available
        if os.getenv("GEN_AI_STUDIO_API_KEY"):
            # Use LLM-enhanced version
            return LLMDatasetQualityMetric().score(arg)
        # Use traditional version
        return DatasetQualityMetric().score(arg)

    # Try to parse a numeric value; on failure, return 0.0
    try:
        v = float(arg)
    except (TypeError, ValueError):
        return 0.0

    # Clamp to [0.0, 1.0] using simple ifs (avoids ternary mistakes)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v
