from ai_model_catalog.metrics.base import Metric


class BusFactorMetric(Metric):
    def score(self, model_data: dict) -> float:
        maintainers = model_data.get("maintainers", [])
        return 1.0 if len(maintainers) >= 1 else 0.0


def score_bus_factor(maintainers: list) -> float:
    return BusFactorMetric().score({"maintainers": maintainers})
