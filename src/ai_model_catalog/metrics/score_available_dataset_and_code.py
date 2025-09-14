from ai_model_catalog.metrics.base import Metric

class AvailabilityMetric(Metric):
    def score(self, model_data: dict) -> float:
        has_code = bool(model_data.get("has_code", True))
        has_dataset = bool(model_data.get("has_dataset", True))
        return 1.0 if has_code and has_dataset else 0.0