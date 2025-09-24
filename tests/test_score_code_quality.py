import pytest

from ai_model_catalog.metrics.score_code_quality import (
    CodeQualityMetric,
    score_code_quality,
)


@pytest.mark.parametrize(
    "readme, expected",
    [
        ("", 0.0),  # no signals
        ("This project uses pytest.", 0.25),  # tests only
        ("pytest + GitHub Actions workflow.", 0.50),  # tests + CI
        ("pytest + workflow + black formatter.", 0.75),  # tests + CI + lint
        ("pytest + workflow + black + mypy", 1.0),  # all four buckets
    ],
)
def test_bucket_counts(readme, expected):
    cls_score = CodeQualityMetric().score({"readme": readme})
    fn_score = score_code_quality({"readme": readme})
    assert cls_score == pytest.approx(expected, abs=1e-12)
    assert fn_score == pytest.approx(expected, abs=1e-12)
    assert 0.0 <= cls_score <= 1.0 and 0.0 <= fn_score <= 1.0


def test_case_insensitive_and_synonyms():
    # Mix keywords with different casing and synonyms
    readme = """Unit Test suite present.
    WORKFLOW set up via CircleCI with build status badge.
    Pre-Commit runs Ruff and Black.
    API Reference on ReadTheDocs."""
    s = CodeQualityMetric().score({"readme": readme})
    assert s == pytest.approx(1.0, abs=1e-12)


def test_missing_readme_defaults_to_zero():
    assert CodeQualityMetric().score({}) == 0.0


def test_numeric_wrapper_path_with_clamping_and_errors():
    assert score_code_quality(0.3) == 0.3  # pass-through
    assert score_code_quality(-0.2) == 0.0  # clamped low
    assert score_code_quality(2.0) == 1.0  # clamped high
    assert score_code_quality("not-a-number") == 0.0  # invalid -> 0.0
