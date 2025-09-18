import pytest

from ai_model_catalog.metrics.score_dataset_quality import (
    DatasetQualityMetric,
    score_dataset_quality,
)


@pytest.mark.parametrize(
    "readme, tags, expected",
    [
        ("", [], 0.0),  # no signals
        ("This uses a dataset.", [], 0.25),  # dataset word only
        ("Trained on ImageNet.", [], 0.25),  # known name only
        ("See [data](http://ex.com) dataset", [], 0.50),  # link + dataset word
        ("dataset and imagenet", [], 0.50),  # dataset word + known name
        ("", ["benchmark"], 0.25),  # tag-only path
        (
            "ImageNet dataset; data http://ex.com",
            ["benchmark"],
            1.0,
        ),  # all four buckets hit
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
    assert s == 0.0


def test_case_insensitive_and_tag_known_names():
    readme = "TRAINED ON CIFAR with DATASET described."
    tags = ["BenchMark", "MNIST"]
    s = DatasetQualityMetric().score({"readme": readme, "tags": tags})
    # dataset word + known name + dataset tag = 3 buckets -> 0.75
    assert s == pytest.approx(0.75, abs=1e-12)


def test_missing_fields_default_to_zero():
    assert DatasetQualityMetric().score({}) == 0.0


def test_numeric_wrapper_path_clamping_and_errors():
    assert score_dataset_quality(0.3) == 0.3
    assert score_dataset_quality(-0.1) == 0.0
    assert score_dataset_quality(2.0) == 1.0
    assert score_dataset_quality("not-a-number") == 0.0
