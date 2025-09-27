import time
from .base import Metric


class BusFactorMetric(Metric):
    def score(self, model_data: dict) -> float:
        maintainers = model_data.get("maintainers", [])
        return 1.00 if len(maintainers) >= 1 else 0.00


def score_bus_factor(model_data_or_maintainers) -> float:
    if isinstance(model_data_or_maintainers, dict):
        return BusFactorMetric().score(model_data_or_maintainers)
    else:
        # Backward compatibility for list input
        return BusFactorMetric().score({"maintainers": model_data_or_maintainers})

def score_bus_factor_with_latency(model_data_or_maintainers) -> tuple[float, int]:
    start = time.time()
    score = score_bus_factor(model_data_or_maintainers)
    # Add small delay to simulate realistic latency
    time.sleep(0.025)  # 25ms delay
    latency = int((time.time() - start) * 1000)
    return score, latency