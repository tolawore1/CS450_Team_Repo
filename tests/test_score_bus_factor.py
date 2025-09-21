import math

import pytest

from ai_model_catalog.metrics.score_bus_factor import (
    BusFactorMetric,
    score_bus_factor,
)


@pytest.mark.parametrize(
    "maintainers, expected",
    [
        ([], 0.0),  # empty list => 0.0
        (["alice"], 1.0),  # one maintainer => 1.0
        (["alice", "bob"], 1.0),  # multiple maintainers => 1.0
        (set(), 0.0),  # empty set behaves like empty list
        ({"alice"}, 1.0),  # non-empty set counts as >=1
    ],
)
def test_bus_factor_values(maintainers, expected):
    got = score_bus_factor(maintainers)  # uses the wrapper
    assert isinstance(got, float)
    assert math.isfinite(got)
    assert 0.0 <= got <= 1.0
    assert got == pytest.approx(expected, abs=1e-12)


def test_wrapper_vs_class_parity():
    data = ["alice", "bob"]
    cls_score = BusFactorMetric().score({"maintainers": data})
    fn_score = score_bus_factor(data)
    assert cls_score == pytest.approx(fn_score, abs=1e-12) == 1.0


def test_missing_key_defaults_to_zero():
    # Direct class call with no 'maintainers' key -> default [] -> 0.0
    assert BusFactorMetric().score({}) == 0.0


def test_none_raises_typeerror():
    # Passing None (not a sequence) triggers len(None) -> TypeError
    with pytest.raises(TypeError):
        BusFactorMetric().score({"maintainers": None})  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        score_bus_factor(None)  # type: ignore[arg-type]


def test_string_is_treated_as_sequence():
    # Current implementation counts any non-empty *sequence* as >=1.
    # A non-empty string therefore returns 1.0.
    assert score_bus_factor("alice") == 1.0  # type: ignore[arg-type]
