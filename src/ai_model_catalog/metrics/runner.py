from __future__ import annotations
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, TextIO
from time import perf_counter

from .base import Metric
from .types import MetricResult


def run_metrics(
    metrics: Iterable[Metric], ctx, max_workers: int = 4
) -> List[MetricResult]:
    results: List[MetricResult] = []

    def _run_one(m: Metric) -> MetricResult:
        t0 = perf_counter()
        try:
            s = float(m.score(ctx))
            s = max(0.0, min(1.0, s))  # clamp to [0, 1]
            name = m.__class__.__name__.replace("Metric", "").lower()
            return MetricResult(
                name=name,
                score=s,
                passed=(s >= 0.5),
                details={},
                error=None,
                elapsed_s=perf_counter() - t0,
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            name = m.__class__.__name__.replace("Metric", "").lower()
            return MetricResult(
                name=name,
                score=0.0,
                passed=False,
                details={},
                error=str(e),
                elapsed_s=perf_counter() - t0,
            )

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {pool.submit(_run_one, m): m for m in metrics}
        for fut in as_completed(futs):
            results.append(fut.result())

    return results


def print_ndjson(results: List[MetricResult], stream: TextIO) -> None:
    for r in results:
        line = {
            "name": r.name,
            "score": r.score,
            "passed": r.passed,
            "latency_s": round(r.elapsed_s, 4),
            "error": r.error,
            **(dict(r.details) if r.details else {}),
        }
        stream.write(json.dumps(line) + "\n")
