# --- stdlib ---
from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict

# --- third-party ---
import typer

from ai_model_catalog import fetch_repo as fr  # <-- module import

# --- local ---
from ..utils import _as_int, _as_bool

log = logging.getLogger(__name__)


@dataclass
class ModelHandler:
    model_id: str

    def fetch_data(self) -> Dict[str, Any]:
        log.info("Fetching HF model data: %s", self.model_id)
        data = fr.fetch_model_data(model_id=self.model_id)
        if not isinstance(data, dict):
            raise TypeError("fetch_model_data() must return a dict")
        return data

    def format_data(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        formatted: Dict[str, Any] = {
            "source": "huggingface",
            "id": raw.get("modelId") or raw.get("id") or self.model_id,
            "author": raw.get("author") or raw.get("owner") or "",
            "license": raw.get("license") or "",
            "downloads": _as_int(raw.get("downloads")),  # mock supplies this
            "last_modified": raw.get("lastModified") or raw.get("last_modified") or "",
            "has_readme": _as_bool(raw.get("readme"))
            or _as_bool(raw.get("has_readme")),
        }

        card = raw.get("cardData")
        if isinstance(card, dict):
            formatted["card_keys"] = sorted(card.keys())[:10]

        return formatted

    def display_data(self, formatted: Dict[str, Any]) -> None:
        typer.echo(json.dumps(formatted, indent=2, ensure_ascii=False))
