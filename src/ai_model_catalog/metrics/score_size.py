from ai_model_catalog.metrics.base import Metric

class SizeMetric(Metric):
    def score(self, model_data: dict) -> float:
        repo_size_bytes = model_data.get("repo_size_bytes")
        if repo_size_bytes is None or repo_size_bytes <= 0:
            return 0.0
        max_size = 1_000_000_000 
        score = max(0.0, 1.0 - repo_size_bytes / max_size)
        return round(score, 3)