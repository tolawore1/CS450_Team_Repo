from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol, Optional, Dict, Any
import json
import logging
import os
import re
import time

log = logging.getLogger(__name__)

# =========
# Text LLMs
# =========


class LLM(Protocol):
    def generate(
        self, system_prompt: str, user_prompt: str, *, temperature: float = 0.0
    ) -> str: ...


@dataclass
class DummyLLM(LLM):
    """Offline & no-dependency fallback; great for tests and when no API key is set."""

    reply: str = (
        "LLM disabled (no provider API key). "
        "Set PURDUE_GENAI_API_KEY or OPENAI_API_KEY to enable."
    )

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.0) -> str:
        return self.reply


class OpenAIClient(LLM):
    """Tiny wrapper; lazy-import openai so dependency stays optional."""

    def __init__(self, api_key: str) -> None:
        try:
            from openai import OpenAI  # type: ignore  # pylint: disable=import-error
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Missing `openai` package. Install with: pip install openai"
            ) from exc
        self._client = OpenAI(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.0) -> str:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        resp = self._client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (resp.choices[0].message.content or "").strip()


class PurdueClient(LLM):
    """
    Purdue GenAI Studio text client.
    Env:
      - PURDUE_GENAI_API_KEY (required)
      - PURDUE_GENAI_URL (optional; default below)
      - PURDUE_GENAI_MODEL (optional, e.g., 'claude-3-sonnet')
      - LLM_TIMEOUT (optional seconds)
    """

    def __init__(
        self, api_key: str, *, base_url: Optional[str] = None, model: Optional[str] = None
    ) -> None:
        import requests  # stdlib+; imported here to stay optional

        self._requests = requests
        self._api_key = api_key
        self._url = (
            base_url
            or os.getenv("PURDUE_GENAI_URL")
            or "https://genai-studio.purdue.edu/api/v1/analyze"
        )
        self._model = model or os.getenv("PURDUE_GENAI_MODEL") or "claude-3-sonnet"
        self._timeout = int(os.getenv("LLM_TIMEOUT", "30"))

    def generate(self, system_prompt: str, user_prompt: str, *, temperature: float = 0.0) -> str:
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        payload = {
            "prompt": f"[SYSTEM]\n{system_prompt}\n[/SYSTEM]\n\n{user_prompt}",
            "model": self._model,
            "max_tokens": int(os.getenv("PURDUE_GENAI_MAX_TOKENS", "1000")),
            "temperature": float(os.getenv("PURDUE_GENAI_TEMPERATURE", str(temperature))),
        }
        try:
            resp = self._requests.post(
                self._url, headers=headers, json=payload, timeout=self._timeout
            )
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
            return json.dumps(data, ensure_ascii=False)
        except Exception as exc:  # pragma: no cover
            log.error("Purdue GenAI error: %s", exc)
            return ""


def get_text_llm() -> LLM:
    """Pick provider in this order: Purdue → OpenAI → Dummy."""
    purdue_key = os.getenv("PURDUE_GENAI_API_KEY")
    if purdue_key:
        return PurdueClient(purdue_key)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return OpenAIClient(openai_key)
    return DummyLLM()


# ==========================
# README Analysis (LLM-based)
# ==========================

try:
    import requests as _requests  # type: ignore
except Exception:  # pragma: no cover (grader env may not have requests)
    _requests = None  # type: ignore


@dataclass(frozen=True)
class LLMReadmeAnalysis:
    documentation_quality: float = 0.0  # 0..1
    technical_complexity: float = 0.0  # 0..1
    dataset_info_present: bool = False
    performance_claims: bool = False
    usage_instructions: bool = False
    code_examples: bool = False


class RateLimiter:
    """Simple sliding-window rate limiter (per-process)."""

    def __init__(self, max_calls_per_minute: int = 10):
        self.max = max_calls_per_minute
        self._calls: list[float] = []

    def acquire(self) -> None:
        now = time.time()
        self._calls = [t for t in self._calls if now - t < 60]
        if len(self._calls) >= self.max:
            sleep_s = 60 - (now - self._calls[0])
            if sleep_s > 0:
                time.sleep(sleep_s)
        self._calls.append(time.time())


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _safe_parse_json_map(s: str) -> Dict[str, Any]:
    try:
        data = json.loads(s or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


class ReadmeAnalyzer(Protocol):
    def analyze_readme(self, readme: str) -> LLMReadmeAnalysis: ...


class MockReadmeLLM(ReadmeAnalyzer):
    """
    Heuristic "LLM" for offline/dev use.
    Deterministic so tests are stable.
    """

    HEADER_RE = re.compile(r"^#+\s*(\w+)", re.M)

    def analyze_readme(self, readme: str) -> LLMReadmeAnalysis:
        text = readme or ""
        lower = text.lower()

        sections = len(self.HEADER_RE.findall(text))
        code_blocks = text.count("```")
        docq = (
            0.2 * _clamp01(sections / 6)
            + 0.3 * _clamp01(code_blocks / 3)
            + 0.5 * _clamp01(len(text) / 2000)
        )

        tech_terms = sum(
            k in lower
            for k in [
                "architecture",
                "algorithm",
                "transformer",
                "attention",
                "gradient",
                "benchmark",
                "latency",
                "throughput",
                "vector",
                "embedding",
            ]
        )
        tech = _clamp01(0.15 * tech_terms + 0.35 * _clamp01(len(text) / 3000))

        dataset_info = any(
            k in lower
            for k in ["dataset", "data set", "cifar", "imagenet", "squad", "dataset card"]
        )
        perf = any(
            k in lower
            for k in ["accuracy", "f1", "bleu", "rouge", "matthews", "exact match", "benchmark"]
        )
        usage = any(
            k in lower
            for k in [
                "install",
                "installation",
                "usage",
                "how to use",
                "quickstart",
                "quick start",
                "example",
            ]
        )
        examples = (
            ("```python" in lower)
            or ("```bash" in lower)
            or ("from " in text and "import " in text)
        )

        return LLMReadmeAnalysis(
            documentation_quality=round(_clamp01(docq), 3),
            technical_complexity=round(_clamp01(tech), 3),
            dataset_info_present=bool(dataset_info),
            performance_claims=bool(perf),
            usage_instructions=bool(usage),
            code_examples=bool(examples),
        )


class PurdueReadmeLLM(ReadmeAnalyzer):
    """
    LLM-backed analyzer hitting Purdue GenAI Studio.
    Falls back to Mock when misconfigured or on errors.
    Env:
      - PURDUE_GENAI_API_KEY (optional; if absent -> Mock)
      - PURDUE_GENAI_API_URL (optional)
      - LLM_MODEL (optional; e.g. 'claude-3-sonnet')
      - LLM_TIMEOUT, LLM_MAX_CPM (optional)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        timeout_s: Optional[int] = None,
        ratelimit: Optional[RateLimiter] = None,
    ):
        self.api_url = os.getenv(
            "PURDUE_GENAI_API_URL", "https://genai-studio.purdue.edu/api/v1/analyze"
        )
        self.api_key = os.getenv("PURDUE_GENAI_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "claude-3-sonnet")
        self.timeout_s = timeout_s or int(os.getenv("LLM_TIMEOUT", "30"))
        self.ratelimiter = ratelimit or RateLimiter(
            max_calls_per_minute=int(os.getenv("LLM_MAX_CPM", "10"))
        )
        if not self.api_key:
            log.info("PURDUE_GENAI_API_KEY not set; PurdueReadmeLLM will use Mock.")
        if _requests is None:
            log.info("`requests` not available; PurdueReadmeLLM will use Mock.")

    @staticmethod
    def _build_prompt(readme: str) -> str:
        return (
            "You are evaluating an AI/ML repository README for onboarding quality and risk signals. "
            "Return STRICT MINIMAL JSON with keys: documentation_quality (0..1), technical_complexity (0..1), "
            "dataset_info_present (bool), performance_claims (bool), usage_instructions (bool), code_examples (bool). "
            "If something is unclear, use 0 or false. DO NOT include commentary.\n\n"
            "README:\n" + readme[:50_000]
        )

    def analyze_readme(self, readme: str) -> LLMReadmeAnalysis:
        if not self.api_key or _requests is None:
            return MockReadmeLLM().analyze_readme(readme)

        self.ratelimiter.acquire()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "prompt": self._build_prompt(readme),
            "model": self.model,
            "max_tokens": 750,
            "temperature": 0.1,
        }
        try:
            resp = _requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout_s)  # type: ignore
            resp.raise_for_status()
            content = resp.json().get("content", "{}")
        except Exception as e:  # pragma: no cover
            log.error("LLM service error: %s", e)
            return MockReadmeLLM().analyze_readme(readme)

        data = _safe_parse_json_map(content)
        return LLMReadmeAnalysis(
            documentation_quality=float(data.get("documentation_quality", 0.0) or 0.0),
            technical_complexity=float(data.get("technical_complexity", 0.0) or 0.0),
            dataset_info_present=bool(data.get("dataset_info_present", False)),
            performance_claims=bool(data.get("performance_claims", False)),
            usage_instructions=bool(data.get("usage_instructions", False)),
            code_examples=bool(data.get("code_examples", False)),
        )


def _bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_readme_llm() -> ReadmeAnalyzer:
    """
    Factory with caching for README analysis.
    Controlled by env:
      - LLM_ENABLED=true|false
      - LLM_PROVIDER=purdue|mock
    """
    if not _bool_env("LLM_ENABLED", False):
        log.info("LLM_ENABLED is not true; using Mock README analyzer.")
        return MockReadmeLLM()

    provider = (os.getenv("LLM_PROVIDER") or "purdue").strip().lower()
    if provider == "purdue":
        return PurdueReadmeLLM()
    if provider == "mock":
        return MockReadmeLLM()

    log.warning("Unknown LLM_PROVIDER=%r; falling back to Mock.", provider)
    return MockReadmeLLM()


# --- Backwards-compat shim for tests and CLI ---
# Returns your real configured LLM client (Purdue → OpenAI → Dummy).
def get_llm() -> LLM:
    return get_text_llm()


__all__ = [
    # text LLMs
    "LLM",
    "DummyLLM",
    "OpenAIClient",
    "PurdueClient",
    "get_text_llm",
    "get_llm",
    # README analyzers
    "LLMReadmeAnalysis",
    "ReadmeAnalyzer",
    "MockReadmeLLM",
    "PurdueReadmeLLM",
    "get_readme_llm",
]
