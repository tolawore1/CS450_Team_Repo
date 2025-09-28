import time
from .base import Metric
from .constants import KNOWN_DATASETS


class AvailableDatasetAndCodeMetric(Metric):
    """Scoring: strict 0 unless clear evidence of open dataset and/or code."""

    def score(self, model_data: dict) -> float:
        readme = (model_data.get("readme") or "").lower()

        # --- Evidence checks ---
        # Look for explicit known open datasets in training statements
        training_lines = [
            line
            for line in readme.splitlines()
            if any(
                ind in line.lower()
                for ind in ["trained on", "training data", "training dataset"]
            )
        ]
        has_open_training_data = any(
            any(ds.lower() in line.lower() for ds in KNOWN_DATASETS)
            for line in training_lines
        )

        # Look for explicit evidence of open codebase (very strict)
        # Must have substantial evidence of THIS model's code, not just general mentions
        code_indicators = ["source code", "implementation", "clone", "git clone"]
        has_open_code = any(indicator in readme for indicator in code_indicators)

        # Check for repository mentions but only if they suggest this model's repository
        repo_indicators = ["repository", "repo"]
        repo_lines = [
            line
            for line in readme.splitlines()
            if any(ind in line.lower() for ind in repo_indicators)
        ]
        has_repo_evidence = any(
            any(
                word in line.lower()
                for word in ["this", "model", "available", "download", "install"]
            )
            for line in repo_lines
        )
        has_open_code = has_open_code or has_repo_evidence

        # Only count as open dataset if it's a KNOWN open dataset, not just any dataset mention
        has_open_dataset = has_open_training_data

        # Allow explicit flags from model_data to override
        if model_data.get("has_code") is True:
            has_open_code = True
        if model_data.get("has_dataset") is True:
            has_open_dataset = True

        # --- Base scoring ---
        if has_open_code and has_open_dataset:
            base_score = 1.0 if has_open_training_data and has_open_code else 0.7
        elif has_open_code or has_open_dataset:
            base_score = 0.3
        else:
            base_score = 0.0

        # --- Clamp small noise ---
        if base_score < 0.05:
            return 0.0
        return round(base_score, 2)


def score_available_dataset_and_code(data_or_flag, has_dataset=None) -> float:
    if isinstance(data_or_flag, dict):
        return AvailableDatasetAndCodeMetric().score(data_or_flag)
    return AvailableDatasetAndCodeMetric().score(
        {"has_code": data_or_flag, "has_dataset": has_dataset}
    )


def score_available_dataset_and_code_with_latency(
    data_or_flag, has_dataset=None
) -> tuple[float, int]:
    start = time.time()
    score = score_available_dataset_and_code(data_or_flag, has_dataset)
    time.sleep(0.015)  # simulate latency
    latency = int((time.time() - start) * 1000)
    return score, latency
