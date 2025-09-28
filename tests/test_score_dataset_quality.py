import pytest

from ai_model_catalog.metrics.score_dataset_quality import (
    DatasetQualityMetric,
    score_dataset_quality,
)


@pytest.mark.parametrize(
    "readme, tags, expected",
    [
        ("", [], 0.0),  # no signals
        ("This uses a dataset.", [], 0.0),  # dataset word only - no open training data
        ("Trained on ImageNet.", [], 0.18),  # known name only - partial credit
        (
            "See [data](http://ex.com) dataset",
            [],
            0.0,
        ),  # link + dataset word - but not in training context
        (
            "dataset and imagenet",
            [],
            0.0,
        ),  # dataset word + known name - but not in training context
        ("", ["benchmark"], 0.0),  # tag-only path - no open training data
        (
            "ImageNet dataset; data http://ex.com",
            ["benchmark"],
            0.0,
        ),  # all buckets - but not in training context
    ],
)
def test_bucket_counts(readme, tags, expected):
    cls_score = DatasetQualityMetric().score({"readme": readme, "tags": tags})
    fn_score = score_dataset_quality({"readme": readme, "tags": tags})
    assert cls_score == pytest.approx(expected, abs=1e-12)
    assert fn_score == pytest.approx(expected, abs=1e-12)
    assert 0.0 <= cls_score <= 1.0 and 0.0 <= fn_score <= 1.0


def test_link_without_dataset_word_does_not_count():
    # data_link requires a link *and* a dataset word
    readme = "Please see http://example.com for more info"
    s = DatasetQualityMetric().score({"readme": readme, "tags": []})
    # No open training data evidence
    assert s == pytest.approx(0.0, abs=1e-12)


def test_case_insensitive_and_tag_known_names():
    readme = "TRAINED ON CIFAR with DATASET described."
    tags = ["BenchMark", "MNIST"]
    s = DatasetQualityMetric().score({"readme": readme, "tags": tags})
    # dataset word + known name + tags - but CIFAR not in known datasets
    assert s == pytest.approx(0.72, abs=1e-12)


def test_missing_fields_default_to_zero():
    assert DatasetQualityMetric().score({}) == 0.0


def test_numeric_wrapper_path_clamping_and_errors():
    assert score_dataset_quality(0.3) == 0.3
    assert score_dataset_quality(-0.1) == 0.0
    assert score_dataset_quality(2.0) == 1.0
    assert score_dataset_quality("not-a-number") == 0.0
