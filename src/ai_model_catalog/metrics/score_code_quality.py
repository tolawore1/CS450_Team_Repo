from ai_model_catalog.metrics.base import Metric


class CodeQualityMetric(Metric):
    def score(self, model_data: dict) -> float:
        return 0.0  # Placeholder for actual code quality logic


def score_code_quality(code_quality: float) -> float:
    return CodeQualityMetric().score({"code_quality": code_quality})
