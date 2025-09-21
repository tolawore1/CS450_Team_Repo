import logging
from typing import Any, Dict

from ai_model_catalog.fetch_repo import fetch_model_data

from ..utils import (
    _display_model_info,
    _display_scores,
    _format_model_data,
)
from .base import BaseHandler

log = logging.getLogger("catalog")


class ModelHandler(BaseHandler):
    """Concrete handler for Hugging Face model data."""

    def __init__(self, model_id: str):
        self.model_id = model_id

    def fetch_data(self) -> Dict[str, Any]:
        log.info("Fetching model data for %s", self.model_id)
        return fetch_model_data(self.model_id)

    def format_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return _format_model_data(data, self.model_id)

    def display_data(
        self, formatted_data: Dict[str, Any], raw_data: Dict[str, Any]
    ) -> None:
        _display_model_info(formatted_data)
        _display_scores(raw_data)
