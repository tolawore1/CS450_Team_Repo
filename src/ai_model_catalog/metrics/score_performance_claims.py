from .base import Metric


class PerformanceClaimsMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "")
        if "state-of-the-art" in readme.lower() or "SOTA" in readme.upper():
            return 1.0
        return 0.0


def score_performance_claims(readme: str) -> float:
    return PerformanceClaimsMetric().score({"readme": readme})
