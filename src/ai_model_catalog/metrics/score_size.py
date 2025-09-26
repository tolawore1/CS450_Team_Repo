import time
from typing import Dict, Tuple

from .base import Metric

# Hardware compatibility thresholds (in bytes)
HARDWARE_THRESHOLDS = {
    "raspberry_pi": 100 * 1024 * 1024,  # 100 MB
    "jetson_nano": 500 * 1024 * 1024,  # 500 MB
    "desktop_pc": 2 * 1024 * 1024 * 1024,  # 2 GB
    "aws_server": 10 * 1024 * 1024 * 1024,  # 10 GB
}


class SizeMetric(Metric):
    def score(self, model_data: dict) -> Dict[str, float]:
        repo_size_bytes = model_data.get("repo_size_bytes")
        if repo_size_bytes is None or repo_size_bytes <= 0:
            return {hardware: 0.0 for hardware in HARDWARE_THRESHOLDS}

        scores = {}
        for hardware, max_size in HARDWARE_THRESHOLDS.items():
            if repo_size_bytes <= max_size:
                # Within limit - score based on utilization (lower utilization = higher score)
                utilization = repo_size_bytes / max_size
                # Score ranges from 1.0 (empty) to 0.6 (at limit)
                scores[hardware] = round(1.0 - (utilization * 0.4), 2)
            else:
                # Over limit - score based on how much over (penalty increases with oversize)
                oversize_ratio = repo_size_bytes / max_size
                # Score decreases more gradually as oversize increases
                scores[hardware] = round(
                    max(0.1, 1.0 - (oversize_ratio - 1.0) * 0.8), 2
                )
        for hardware in HARDWARE_THRESHOLDS:
            if hardware not in scores:
                scores[hardware] = 0.0
            # Ensure the value is a float, not boolean
            scores[hardware] = float(scores[hardware])

        return scores


def score_size(repo_size_bytes: int) -> Dict[str, float]:
    return SizeMetric().score({"repo_size_bytes": repo_size_bytes})


def score_size_with_latency(repo_size_bytes: int) -> Tuple[Dict[str, float], int]:
    """Score size with latency in milliseconds."""
    start_time = time.time()
    result = SizeMetric().score({"repo_size_bytes": repo_size_bytes})
    latency = int((time.time() - start_time) * 1000)
    return result, latency
