from typing import Dict
from ai_model_catalog.metrics.base import Metric

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
                # Score ranges from 1.0 (empty) to 0.8 (at limit)
                scores[hardware] = round(1.0 - (utilization * 0.2), 3)
            else:
                # Over limit - score based on how much over (penalty increases with oversize)
                oversize_ratio = repo_size_bytes / max_size
                # Score decreases rapidly as oversize increases
                scores[hardware] = round(max(0.0, 1.0 - (oversize_ratio - 1.0) * 2), 3)

        return scores


def score_size(repo_size_bytes: int) -> Dict[str, float]:
    return SizeMetric().score({"repo_size_bytes": repo_size_bytes})
