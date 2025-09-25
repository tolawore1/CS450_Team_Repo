from __future__ import annotations

from typing import Iterable, Union

from .base import Metric


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    t = (text or "").lower()
    return any(n.lower() in t for n in needles)


class CodeQualityMetric(Metric):
    """Code quality heuristic."""

    def score(self, model_data: dict) -> float:
        readme = model_data.get("readme", "")

        has_tests = _contains_any(
            readme, ["pytest", "unittest", "unit test", "integration test", "tests/"]
        )
        has_ci = _contains_any(
            readme,
            [
                "github actions",
                "workflow",
                "ci",
                "travis",
                "circleci",
                "appveyor",
                "build status",
                "badge",
            ],
        )
        has_lint = _contains_any(
            readme, ["pylint", "flake8", "ruff", "black", "isort", "pre-commit"]
        )
        typing_or_docs = _contains_any(
            readme, ["mypy", "type hints", "typed"]
        ) or _contains_any(
            readme, ["docs/", "documentation", "readthedocs", "api reference"]
        )

        hits = sum([has_tests, has_ci, has_lint, typing_or_docs])
        return max(0.0, min(1.0, hits / 4.0))


def score_code_quality(arg: Union[dict, float]) -> float:
    if isinstance(arg, dict):
        return CodeQualityMetric().score(arg)
    try:
        v = float(arg)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
