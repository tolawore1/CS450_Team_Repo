from ai_model_catalog.metrics.base import Metric

class PerformanceClaimsMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "")
        if "state-of-the-art" in readme.lower() or "SOTA" in readme.upper():
            return 1.0
        return 0.0