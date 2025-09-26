import time
from .base import Metric


class AvailableDatasetAndCodeMetric(Metric):
    def score(self, model_data: dict) -> float:
        has_code = bool(model_data.get("has_code", True))
        has_dataset = bool(model_data.get("has_dataset", True))
        return 1.0 if has_code and has_dataset else 0.0


def score_available_dataset_and_code(has_code: bool, has_dataset: bool) -> float:
    return AvailableDatasetAndCodeMetric().score(
        {"has_code": has_code, "has_dataset": has_dataset}
    )


def score_available_dataset_and_code_with_latency(has_code: bool, has_dataset: bool) -> tuple[float, int]:
    start = time.time()
    score = score_available_dataset_and_code(has_code, has_dataset)
    # Add small delay to simulate realistic latency
    time.sleep(0.015)  # 15ms delay
    latency = int((time.time() - start) * 1000)
    return score, latency

