from ai_model_catalog.metrics.base import Metric


class RampUpMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "")
        if not readme or len(readme) < 250:
            return 0.0
        return 1.0


def score_ramp_up_time(readme: str) -> float:
    return RampUpMetric().score({"readme": readme})
