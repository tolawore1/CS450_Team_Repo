from ai_model_catalog.metrics.base import Metric

class RampUpMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "")
        if not readme or len(readme) < 250:
            return 0.0
        elif len(readme) > 1500:
            return 1.0
        else:
            return 1.0
        