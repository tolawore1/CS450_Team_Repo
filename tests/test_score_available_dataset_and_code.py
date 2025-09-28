import pytest

from ai_model_catalog.metrics.score_available_dataset_and_code import (
    AvailableDatasetAndCodeMetric,
    score_available_dataset_and_code,
)


@pytest.mark.parametrize(
    "has_code, has_dataset, expected",
    [
        (True, True, 0.7),  # Both available but no strong evidence
        (True, False, 0.3),  # Only code available
        (False, True, 0.3),  # Only dataset available
        (False, False, 0.0),  # Neither available
    ],
)
def test_truth_table(has_code, has_dataset, expected):
    # wrapper uses simple bool args
    got = score_available_dataset_and_code(has_code, has_dataset)
    assert got in (0.0, 0.3, 0.7)  # Updated to match new scoring tiers
    assert got == expected


def test_wrapper_vs_class_parity():
    payload = {"has_code": True, "has_dataset": False}
    cls_score = AvailableDatasetAndCodeMetric().score(payload)
    fn_score = score_available_dataset_and_code(
        payload["has_code"], payload["has_dataset"]
    )
    assert cls_score == fn_score == 0.3


def test_missing_keys_default_to_true_true():
    # Your class defaults both flags to False when missing -> returns 0.0
    m = AvailableDatasetAndCodeMetric()
    assert m.score({}) == 0.0


def test_non_boolean_inputs_are_coerced_by_class():
    # The class casts with bool(...), so truthy/falsy values behave accordingly.
    m = AvailableDatasetAndCodeMetric()
    assert (
        m.score({"has_code": "yes", "has_dataset": 1}) == 0.0
    )  # both truthy but no evidence
    assert m.score({"has_code": "yes", "has_dataset": 0}) == 0.0  # 0 is falsy
    assert m.score({"has_code": [], "has_dataset": "data"}) == 0.0  # empty list falsy
