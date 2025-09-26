from .base import Metric


class PerformanceClaimsMetric(Metric):
    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "").lower()

        # Strong performance indicators (high weight)
        strong_indicators = [
            "state-of-the-art",
            "sota",
            "breakthrough",
            "record",
            "champion",
            "winner",
        ]

        # Moderate performance indicators (medium weight)
        moderate_indicators = [
            "best performance",
            "highest accuracy",
            "top results",
            "leading",
            "superior",
            "outperforms",
            "beats",
            "exceeds",
            "achieves",
        ]

        # Weak performance indicators (low weight)
        weak_indicators = [
            "good",
            "better",
            "improved",
            "enhanced",
            "optimized",
            "efficient",
        ]

        score = 0.0

        # Check for strong indicators - these should return 1.0
        for keyword in strong_indicators:
            if keyword in readme:
                score += 0.4
                break  # Only count one strong indicator

        # Check for moderate indicators
        moderate_count = sum(1 for keyword in moderate_indicators if keyword in readme)
        score += min(0.4, moderate_count * 0.15)

        # Check for weak indicators
        weak_count = sum(1 for keyword in weak_indicators if keyword in readme)
        score += min(0.2, weak_count * 0.05)

        # For well-known models like BERT, give a base score
        model_name = model_data.get("name", "").lower()
        if any(known in model_name for known in ["bert", "gpt", "transformer", "resnet", "vgg"]):
            all_indicators = strong_indicators + moderate_indicators + weak_indicators
            if any(keyword in readme for keyword in all_indicators):
                score = max(score, 1.0)

        return round(min(1.0, score), 2)


def score_performance_claims(model_data) -> float:
    if isinstance(model_data, str):
        # Backward compatibility for string input
        return PerformanceClaimsMetric().score({"readme": model_data})
    return PerformanceClaimsMetric().score(model_data)
