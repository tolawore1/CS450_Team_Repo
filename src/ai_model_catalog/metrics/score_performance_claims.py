import time
from .base import Metric

class PerformanceClaimsMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "").lower()

        strong_indicators = [
            "state-of-the-art", "sota", "breakthrough", "record", "champion", "winner",
        ]
        moderate_indicators = [
            "best performance", "highest accuracy", "top results", "leading",
            "superior", "outperforms", "beats", "exceeds", "achieves",
        ]
        weak_indicators = [
            "good", "better", "improved", "enhanced", "optimized", "efficient",
        ]

        score = 0.0

        # Strong indicator: max 0.4
        for keyword in strong_indicators:
            if keyword in readme:
                score += 0.4
                break

        # Moderate indicators: max 0.4
        moderate_count = sum(1 for keyword in moderate_indicators if keyword in readme)
        score += min(0.4, moderate_count * 0.15)

        # Weak indicators: max 0.2
        weak_count = sum(1 for keyword in weak_indicators if keyword in readme)
        score += min(0.2, weak_count * 0.05)

        return round(min(1.0, max(0.0, score)), 2)


def score_performance_claims(model_data) -> float:
    if isinstance(model_data, str):
        return PerformanceClaimsMetric().score({"readme": model_data})
    return PerformanceClaimsMetric().score(model_data)


def score_performance_claims_with_latency(model_data) -> tuple[float, int]:
    start = time.time()
    score = score_performance_claims(model_data)
    latency = int((time.time() - start) * 1000)
    return score, latency
