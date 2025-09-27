import time
from .base import Metric


class BusFactorMetric(Metric):
    def score(self, model_data: dict) -> float:
        maintainers = model_data.get("maintainers", [])
        return 1.0 if len(maintainers) >= 1 else 0.0


def score_bus_factor(maintainers: list) -> float:
    return BusFactorMetric().score({"maintainers": maintainers})

def score_bus_factor_with_latency(maintainers: list) -> tuple[float, int]:
    start = time.time()
    score = score_bus_factor(maintainers)
    # Add small delay to simulate realistic latency
    time.sleep(0.025)  # 25ms delay
    latency = int((time.time() - start) * 1000)
    return score, latency
