import math

import pytest

from ai_model_catalog.metrics.score_ramp_up_time import (
    RampUpMetric,
    score_ramp_up_time,
)


@pytest.mark.parametrize(
    "readme, expected",
    [
        ("", 0.0),  # empty
        ("a" * 1, 0.0),  # tiny
        ("a" * 249, 0.0),  # just below threshold
        ("a" * 250, 1.0),  # boundary
        ("a" * 300, 1.0),  # above threshold
        (" " * 300, 1.0),  # whitespace still counts toward length
    ],
)
def test_len_based_ramp_up_scores(readme, expected):
    got = score_ramp_up_time(readme)
    assert isinstance(got, float)
    assert math.isfinite(got)
    assert 0.0 <= got <= 1.0
    assert got == pytest.approx(expected, abs=1e-12)


def test_wrapper_vs_class_parity():
    long_readme = "x" * 500
    cls_score = RampUpMetric().score({"readme": long_readme})
    fn_score = score_ramp_up_time(long_readme)
    assert cls_score == pytest.approx(fn_score, abs=1e-12) == 1.0


def test_missing_key_defaults_to_zero():
    # Direct class call with no 'readme' key returns 0.0
    assert RampUpMetric().score({}) == 0.0


def test_none_is_treated_as_empty():
    # Wrapper accepts None at runtime (despite type hint) and returns 0.0
    assert score_ramp_up_time(None) == 0.0  # type: ignore[arg-type]


def test_non_string_readme_raises_typeerror():
    # Non-string truthy value will reach len(...) and raise TypeError
    with pytest.raises(TypeError):
        RampUpMetric().score({"readme": 123})  # type: ignore[arg-type]
