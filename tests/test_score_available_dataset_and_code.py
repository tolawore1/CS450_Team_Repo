import pytest

from ai_model_catalog.metrics.score_available_dataset_and_code import (
    AvailableDatasetAndCodeMetric,
    score_available_dataset_and_code,
)


@pytest.mark.parametrize(
    "has_code, has_dataset, expected",
    [
        (True, True, 1.0),
        (True, False, 0.0),
        (False, True, 0.0),
        (False, False, 0.0),
    ],
)
def test_truth_table(has_code, has_dataset, expected):
    # wrapper uses simple bool args
    got = score_available_dataset_and_code(has_code, has_dataset)
    assert got in (0.0, 1.0)
    assert got == expected


def test_wrapper_vs_class_parity():
    payload = {"has_code": True, "has_dataset": False}
    cls_score = AvailableDatasetAndCodeMetric().score(payload)
    fn_score = score_available_dataset_and_code(
        payload["has_code"], payload["has_dataset"]
    )
    assert cls_score == fn_score == 0.0


def test_missing_keys_default_to_true_true():
    # Your class defaults both flags to True when missing -> returns 1.0
    m = AvailableDatasetAndCodeMetric()
    assert m.score({}) == 1.0


def test_non_boolean_inputs_are_coerced_by_class():
    # The class casts with bool(...), so truthy/falsy values behave accordingly.
    m = AvailableDatasetAndCodeMetric()
    assert m.score({"has_code": "yes", "has_dataset": 1}) == 1.0  # both truthy
    assert m.score({"has_code": "yes", "has_dataset": 0}) == 0.0  # 0 is falsy
    assert m.score({"has_code": [], "has_dataset": "data"}) == 0.0  # empty list falsy
