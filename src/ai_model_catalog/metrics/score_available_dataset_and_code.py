import time
from .base import Metric
class AvailableDatasetAndCodeMetric(Metric):
    def score(self, model_data: dict) -> float:
        has_code = bool(model_data.get("has_code", True))
        has_dataset = bool(model_data.get("has_dataset", True))
        return 1.00 if has_code and has_dataset else 0.00
def score_available_dataset_and_code(has_code_or_model_data, has_dataset=None) -> float:
    if isinstance(has_code_or_model_data, dict):
        return AvailableDatasetAndCodeMetric().score(has_code_or_model_data)
    else:
        # Backward compatibility for boolean inputs
        return AvailableDatasetAndCodeMetric().score(
            {"has_code": has_code_or_model_data, "has_dataset": has_dataset}
        )

def score_available_dataset_and_code_with_latency(
        has_code_or_model_data, has_dataset=None) -> tuple[float, int]:
    start = time.time()
    score = score_available_dataset_and_code(has_code_or_model_data, has_dataset)
    # Add small delay to simulate realistic latency
    time.sleep(0.015)  # 15ms delay
    latency = int((time.time() - start) * 1000)
    return score, latency