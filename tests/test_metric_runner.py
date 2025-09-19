import io
import json
import math
import time

from ai_model_catalog.metrics.base import Metric
from ai_model_catalog.metrics.runner import print_ndjson, run_metrics
from ai_model_catalog.metrics.types import MetricResult

# --- Fake metrics for concurrency/clamping/error tests ------------------------


class OverMetric(Metric):
    def name(self) -> str:
        return "over"

    def score(self, model_data) -> float:
        _ = model_data  # silence unused-argument
        return 1.5  # should be clamped to 1.0


class UnderMetric(Metric):
    def name(self) -> str:
        return "under"

    def score(self, model_data) -> float:
        _ = model_data
        return -0.2  # should be clamped to 0.0


class HalfMetric(Metric):
    def name(self) -> str:
        return "half"

    def score(self, model_data) -> float:
        _ = model_data
        return 0.5  # right on the pass threshold


class SlowMetric(Metric):
    def name(self) -> str:
        return "slow"

    def score(self, model_data) -> float:
        _ = model_data
        time.sleep(0.02)
        return 0.9


class BoomMetric(Metric):
    def name(self) -> str:
        return "boom"

    def score(self, model_data) -> float:
        _ = model_data
        raise RuntimeError("boom!")


# --- Tests for run_metrics ----------------------------------------------------


def _results_by_name(results):
    """Index results by metric name derived from class name."""
    return {r.name: r for r in results}


def test_run_metrics_clamping_and_pass_fail():
    metrics = [OverMetric(), UnderMetric(), HalfMetric()]
    res = run_metrics(metrics, ctx={}, max_workers=3)
    by = _results_by_name(res)

    assert set(by.keys()) == {"over", "under", "half"}

    assert by["over"].score == 1.0 and by["over"].passed is True
    assert by["under"].score == 0.0 and by["under"].passed is False
    assert by["half"].score == 0.5 and by["half"].passed is True

    for r in res:
        assert isinstance(r.elapsed_s, float) and r.elapsed_s >= 0.0
        assert r.error in (None, r.error)  # field exists


def test_run_metrics_handles_exceptions_and_latency():
    metrics = [SlowMetric(), BoomMetric()]
    res = run_metrics(metrics, ctx={}, max_workers=2)
    by = _results_by_name(res)

    assert math.isclose(by["slow"].score, 0.9, abs_tol=1e-12)
    assert by["slow"].passed is True
    assert by["slow"].error is None
    assert by["slow"].elapsed_s >= 0.015  # should reflect the sleep

    assert by["boom"].score == 0.0
    assert by["boom"].passed is False
    assert isinstance(by["boom"].error, str) and "boom" in by["boom"].error.lower()


# --- Tests for print_ndjson ---------------------------------------------------


def test_print_ndjson_emits_one_line_per_result_and_flattens_details():
    r1 = MetricResult(
        name="alpha",
        score=0.75,
        passed=True,
        details={"extra": 42, "tag": "ok"},
        error=None,
        elapsed_s=0.01236,  # rounds to 4 dp => 0.0124
    )
    r2 = MetricResult(
        name="beta",
        score=0.0,
        passed=False,
        details={},
        error="oops",
        elapsed_s=0.0,
    )

    buf = io.StringIO()
    print_ndjson([r1, r2], buf)
    out = buf.getvalue()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 2

    row1 = json.loads(lines[0])
    row2 = json.loads(lines[1])

    for row in (row1, row2):
        assert {"name", "score", "passed", "latency_s", "error"} <= set(row.keys())

    assert "extra" in row1 and row1["extra"] == 42
    assert "tag" in row1 and row1["tag"] == "ok"
    assert "details" not in row1

    assert row1["latency_s"] == 0.0124
    assert row2["latency_s"] == 0.0

    assert row1["name"] == "alpha" and row1["score"] == 0.75 and row1["passed"] is True
    assert row2["name"] == "beta" and row2["score"] == 0.0 and row2["passed"] is False
    assert isinstance(row2["error"], str) and "oops" in row2["error"]
