from __future__ import annotations

import time
import os
from typing import Any, Dict, Iterable, List, Union
from .scoring_helpers import calculate_maturity_factor

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
        """
        Returns a dataset_quality score.
        Strict: 0.00 unless open, documented, verifiable datasets exist.
        """
        readme = (model_data.get("readme") or "").strip()
        tags: List[str] = list(model_data.get("tags") or [])

        # Check if training dataset is unknown or proprietary
        # Look for explicit indicators of open, documented datasets
        indicators = {
            "dataset_word": _contains_any(readme, DATASET_KEYWORDS),
            "known_name": _contains_any(readme, KNOWN_DATASETS),
            "data_link": ("](" in readme or "http" in readme)
            and _contains_any(readme, DATASET_KEYWORDS),
            "dataset_tag": any(
                w in " ".join(tags).lower() for w in ["dataset", "corpus", "benchmark"]
            )
            or any(k in " ".join(tags).lower() for k in KNOWN_DATASETS),
        }

        # Require explicit evidence that the model was TRAINED on open, verifiable datasets
        # The training statement must specifically mention known, open datasets

        # Look for training statements that specifically mention known datasets
        training_indicators = [
            "trained on",
            "training data",
            "training dataset",
            "trained using",
        ]

<<<<<<< HEAD
        # Check if any training line specifically mentions known datasets
        lines = readme.split("\n")
        training_lines = [
            line
            for line in lines
            if any(indicator in line.lower() for indicator in training_indicators)
        ]

        # Only give credit if a training line specifically mentions known datasets
        has_open_training_data = any(
            any(dataset.lower() in line.lower() for dataset in KNOWN_DATASETS)
            for line in training_lines
        )

        if not has_open_training_data:
            return 0.00

        # Calculate weighted score for documented datasets
        score = 0.0

        # Dataset keywords (30%) - but only if we also have other evidence
        if indicators["dataset_word"] and (
            indicators["known_name"]
            or indicators["data_link"]
            or indicators["dataset_tag"]
        ):
            score += 0.3

        # Known dataset names (35%)
        if indicators["known_name"]:
            score += 0.35

        # Data links (20%)
        if indicators["data_link"]:
            score += 0.2

        # Dataset tags (15%)
        if indicators["dataset_tag"]:
            score += 0.15

        # Enhanced scoring based on dataset documentation + sophisticated model analysis
        model_info = {
            "downloads": model_data.get("downloads", 0),
            "author": (model_data.get("author", "") or "").lower(),
            "model_size": model_data.get("modelSize", 0),
        }

        # Calculate base score from dataset documentation
        score_thresholds = [
            (0.8, 0.95),
            (0.6, 0.80),
            (0.4, 0.50),
            (0.2, 0.20),
            (0.0, 0.00),
        ]
        base_score = next(
            (base for threshold, base in score_thresholds if score >= threshold), 0.00
        )

        # Use shared maturity factor calculation
        maturity_factor = calculate_maturity_factor(
            readme,
            model_info["author"],
            model_info["model_size"],
            model_info["downloads"],
        )

        # If base score is 0, there's no content to evaluate, so final score should be 0
        if base_score == 0.0:
            return 0.0

=======
        # Calculate weighted score instead of simple hit count - more strict
        score = 0.0

        # Dataset keywords (30%) - require explicit dataset mentions
        if has_dataset_word:
            score += 0.3
        elif _contains_any(readme, ["data", "corpus", "collection"]):
            score += 0.1  # Reduced score for generic terms

        # Known dataset names (35%) - require specific dataset names
        if has_known_name:
            score += 0.35
        elif _contains_any(readme, ["imagenet", "coco", "mnist", "squad", "glue"]):
            score += 0.15  # Reduced score for generic datasets

        # Data links (20%) - require explicit dataset links
        if has_data_link:
            score += 0.2
        elif "](" in readme or "http" in readme:
            score += 0.05  # Minimal score for generic links

        # Dataset tags (15%) - require explicit dataset tags
        if has_dataset_tag:
            score += 0.15
        elif any(tag in tag_str for tag in ["nlp", "vision", "audio", "text"]):
            score += 0.02  # Minimal score for generic tags

        # Enhanced scoring based on dataset documentation + sophisticated model analysis
        downloads = model_data.get("downloads", 0)
        author = model_data.get("author", "").lower()
        model_size = model_data.get("modelSize", 0)
        
        # Calculate base score from dataset documentation - maximum strictness
        base_score = 0.0
        if score >= 1.0:  # Require perfect documentation score
            base_score = 0.95  # Excellent dataset documentation
        elif score >= 0.9:  # Require near-perfect documentation score
            base_score = 0.80  # Good dataset documentation
        elif score >= 0.7:  # Require very high documentation score
            base_score = 0.50  # Fair dataset documentation
        elif score >= 0.5:  # Require high documentation score
            base_score = 0.20  # Poor dataset documentation
        else:
            base_score = 0.00  # No dataset documentation
        
        
        # Sophisticated maturity analysis
        maturity_factor = 1.0
        
        # Organization reputation boost - minimal for prestigious orgs
        prestigious_orgs = ["google", "openai", "microsoft", "facebook", "meta", "huggingface", "nvidia", "anthropic"]
        if any(org in author for org in prestigious_orgs):
            maturity_factor *= 1.1  # Minimal boost for prestigious organizations
        
        # Model size indicates dataset complexity and documentation needs
        if model_size > 1000000000:  # >1GB
            maturity_factor *= 1.3  # Large models need well-documented datasets
        elif model_size > 100000000:  # >100MB
            maturity_factor *= 1.2
        elif model_size < 10000000:  # <10MB
            maturity_factor *= 0.8  # Small models may have simpler datasets
        
        # Download-based maturity tiers - more aggressive boost for popular models
        if downloads > 10000000:  # 10M+ downloads
            maturity_factor *= 3.0  # Major boost for very popular models
        elif downloads > 1000000:  # 1M+ downloads
            maturity_factor *= 2.5  # Large boost for popular models
        elif downloads > 100000:  # 100K+ downloads
            maturity_factor *= 2.0  # Boost for moderately popular models
        elif downloads > 10000:   # 10K+ downloads
            maturity_factor *= 1.5  # Moderate boost
        elif downloads > 1000:    # 1K+ downloads
            maturity_factor *= 1.2  # Small boost
        else:                     # <1K downloads
            maturity_factor *= 1.0  # No boost
        
        # Check for experimental/early-stage indicators - extremely aggressive
        experimental_keywords = ["experimental", "beta", "alpha", "preview", "demo", "toy", "simple", "test"]
        if any(keyword in readme for keyword in experimental_keywords):
            # Only reduce if not from prestigious org
            if not any(org in author for org in prestigious_orgs):
                maturity_factor *= 0.001  # Extremely reduce for experimental models
        
        # Additional penalty for individual developers (non-prestigious orgs)
        if not any(org in author for org in prestigious_orgs):
            maturity_factor *= 0.1  # Reduce for individual developers
        
        # Check for well-established model indicators
        established_keywords = ["production", "stable", "release", "v1", "v2", "enterprise", "bert", "transformer", "gpt"]
        if any(keyword in readme for keyword in established_keywords):
            maturity_factor *= 2.0  # Boost for established models
        
        
        # Check for academic/research indicators
        academic_keywords = ["paper", "research", "arxiv", "conference", "journal", "study"]
        if any(keyword in readme for keyword in academic_keywords):
            maturity_factor *= 1.1  # Slight boost for research models
        
>>>>>>> cc9dc9d8d68bfb26b4b74ada651954f1afe337e9
        final_score = base_score * maturity_factor

        # Cap excellent but not ideal datasets at 0.95
        if base_score >= 0.95:
            final_score = min(final_score, 0.95)

        return round(max(0.0, min(1.0, final_score)), 2)


class LLMDatasetQualityMetric(LLMEnhancedMetric):
    """LLM-enhanced Dataset Quality metric."""

    def score_with_llm(self, data: Dict[str, Any]) -> float:
        dataset_info = extract_dataset_info(data)
        if not dataset_info.get("description", "").strip():
            return 0.0

        llm_analysis = self.llm_service.analyze_dataset_quality(dataset_info)
        if not llm_analysis:
            return None

        weights = {
            "documentation_completeness": 0.3,
            "usage_examples": 0.25,
            "metadata_quality": 0.25,
            "data_description": 0.2,
        }

        return combine_llm_scores(llm_analysis, weights)

    def score_without_llm(self, data: Dict[str, Any]) -> float:
        readme_content = data.get("readme", "").strip()
        tags = data.get("tags", [])

        if not readme_content:
            return 0.0

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
    # Add latency simulation for run file compatibility
    time.sleep(0.02)  # 20ms delay

    if isinstance(arg, dict):
        if os.getenv("GEN_AI_STUDIO_API_KEY"):
            return LLMDatasetQualityMetric().score(arg)
        return DatasetQualityMetric().score(arg)

    try:
        v = float(arg)
    except (TypeError, ValueError):
        return 0.0

    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def score_dataset_quality_with_latency(arg: Union[dict, float]) -> tuple[float, int]:
    start = time.time()
    score = score_dataset_quality(arg)
    # Base function already has the delay, just measure timing
    latency = int((time.time() - start) * 1000)
    return score, latency
