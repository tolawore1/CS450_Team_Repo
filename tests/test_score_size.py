import pytest

from ai_model_catalog.metrics.score_size import SizeMetric, score_size


def test_zero_and_negative_return_zero():
    assert score_size(0) == 0.0
    assert score_size(-123) == 0.0

    m = SizeMetric()
    assert m.score({"repo_size_bytes": None}) == 0.0
    assert m.score({"repo_size_bytes": 0}) == 0.0


def test_small_sizes_round_to_one():
    # 1 KB -> 1 - 1e-6 ≈ 0.999999 -> rounded to 1.0
    assert score_size(1_000) == 1.0


def test_mid_value_rounding_example():
    # 123_456_789 bytes -> 1 - 0.123456789 = 0.876543211 -> round(..., 3) == 0.877
    assert score_size(123_456_789) == 0.877


def test_boundary_and_near_max():
    assert score_size(1_000_000_000) == 0.0  # exactly max -> 0.0
    assert score_size(999_000_000) == 0.001  # 1 - 0.999 = 0.001


def test_above_max_saturates_to_zero():
    assert score_size(2_000_000_000) == 0.0
    assert score_size(5_000_000_000) == 0.0


def test_monotonic_small_vs_large():
    small = score_size(10_000_000)  # 10 MB
    large = score_size(600_000_000)  # 600 MB
    assert 0.0 <= small <= 1.0
    assert 0.0 <= large <= 1.0
    assert small >= large  # smaller repo should not score worse


def test_wrapper_vs_class_parity():
    b = 500_000_000
    cls_score = SizeMetric().score({"repo_size_bytes": b})
    fn_score = score_size(b)
    assert cls_score == fn_score


def test_invalid_type_raises_typeerror():
    with pytest.raises(TypeError):
        SizeMetric().score({"repo_size_bytes": "100"})  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        score_size("100")  # type: ignore[arg-type]
