# --- stdlib ---
from __future__ import annotations
import json
import logging
from typing import Any, Dict

from ai_model_catalog.fetch_repo import fetch_repo_data
from ai_model_catalog.score_model import score_repo_from_owner_and_repo

from ..utils import (
    _display_repository_info,
    _display_scores,
    _format_repository_data,
    _get_repository_counts_info,
)
from .base import BaseHandler
# --- third-party ---
import typer

# --- local ---
from ai_model_catalog import (
    fetch_repo as fr,
)  # <-- module import (pytest can monkeypatch)

log = logging.getLogger(__name__)


@dataclass
class RepositoryHandler:
    owner: str
    repo: str

    def fetch_data(self) -> Dict[str, Any]:
        log.info("Fetching repo data: %s/%s", self.owner, self.repo)
        data = fr.fetch_repo_data(owner=self.owner, repo=self.repo)
        if not isinstance(data, dict):
            raise TypeError("fetch_repo_data() must return a dict")
        return data

    def format_data(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        def _as_int(v: Any, default: int = 0) -> int:
            try:
                return int(v)
            except Exception:
                return default

        def _as_bool(v: Any) -> bool:
            return bool(v) and str(v).strip().lower() not in {
                "",
                "false",
                "0",
                "none",
                "null",
            }

        # owner may be a dict from GitHub API
        owner_val = raw.get("author") or raw.get("owner") or ""
        if isinstance(owner_val, dict):
            owner_val = owner_val.get("login") or owner_val.get("name") or ""

        license_val = raw.get("license")
        if isinstance(license_val, dict):
            license_val = license_val.get("spdx_id") or license_val.get("key") or ""

        formatted: Dict[str, Any] = {
            "source": "github",
            "full_name": f"{self.owner}/{self.repo}",
            "id": raw.get("id") or raw.get("name") or f"{self.owner}/{self.repo}",
            "author": owner_val or "",
            "license": license_val or "",
            "downloads": _as_int(raw.get("downloads")),  # mock supplies this
            "commits_count": _as_int(raw.get("commits_count")),  # mock supplies this
            "last_modified": raw.get("last_modified")
            or raw.get("pushed_at")
            or raw.get("updated_at")
            or "",
            "has_readme": _as_bool(raw.get("readme"))
            or _as_bool(raw.get("has_readme")),
        }

        for k in ("description", "topics", "tags", "default_branch"):
            if k in raw:
                formatted[k] = raw[k]

        return formatted

    def display_data(
        self, formatted: Dict[str, Any], raw: Optional[Dict[str, Any]] = None
    ) -> None:
        # Always output JSON (prevents dict formatting errors)
        typer.echo(json.dumps(formatted, indent=2, ensure_ascii=False))
