from ai_model_catalog.metrics.base import Metric


class DatasetQualityMetric(Metric):
    def score(self, model_data: dict) -> float:
        return 0.0  # Placeholder for actual dataset quality logic


def score_dataset_quality(dataset_quality: float) -> float:
    return DatasetQualityMetric().score({"dataset_quality": dataset_quality})
