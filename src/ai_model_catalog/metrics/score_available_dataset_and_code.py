from .base import Metric


class AvailableDatasetAndCodeMetric(Metric):
    def score(self, model_data: dict) -> float:
        has_code = bool(model_data.get("has_code", True))
        has_dataset = bool(model_data.get("has_dataset", True))
        return 1.0 if has_code and has_dataset else 0.0


def score_available_dataset_and_code(has_code: bool, has_dataset: bool) -> float:
    return AvailableDatasetAndCodeMetric().score(
        {"has_code": has_code, "has_dataset": has_dataset}
    )
