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

        #Prevent crash if passed a bool or invalid value
        if not isinstance(repo_size_bytes, (int, float)) or repo_size_bytes <= 0:
            return {hardware: 0.0 for hardware in HARDWARE_THRESHOLDS}

        scores = {}
        for hardware, max_size in HARDWARE_THRESHOLDS.items():
            if repo_size_bytes <= max_size:
                utilization = repo_size_bytes / max_size
                # ✅ Adjusted curve: less harsh penalty
                scores[hardware] = round(1.0 - (utilization * 0.3), 2)
            else:
                oversize_ratio = repo_size_bytes / max_size
                scores[hardware] = round(
                    max(0.1, 1.0 - (oversize_ratio - 1.0) * 0.8), 2
                )

        # Ensure all values are float and not bool
        for hardware in HARDWARE_THRESHOLDS:
            if hardware not in scores:
                scores[hardware] = 0.0
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
