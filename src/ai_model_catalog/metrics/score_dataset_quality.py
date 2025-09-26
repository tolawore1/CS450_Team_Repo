from __future__ import annotations

from typing import Iterable, List, Union

from .base import Metric
from .constants import DATASET_KEYWORDS, KNOWN_DATASETS


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

        hits = (
            int(has_dataset_word)
            + int(has_known_name)
            + int(has_data_link)
            + int(has_dataset_tag)
        )
        # Normalize to [0, 1]
        return max(0.0, min(1.0, hits / 4.0))


def score_dataset_quality(arg: Union[dict, float]) -> float:
    """Wrapper that accepts either a model_data dict or a raw float and clamps to [0.0, 1.0]."""
    if isinstance(arg, dict):
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
