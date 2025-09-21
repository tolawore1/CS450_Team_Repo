import logging
from typing import Any, Dict

import typer
from ai_model_catalog.fetch_repo import fetch_repo_data
from .base import BaseHandler
from ..utils import (
    _format_repository_data,
    _get_repository_counts_info,
    _display_repository_info,
    _display_scores,
)

log = logging.getLogger("catalog")


class RepositoryHandler(BaseHandler):
    """Concrete handler for GitHub repository data."""

    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo

    def fetch_data(self) -> Dict[str, Any]:
        log.info("Fetching repository data for %s/%s", self.owner, self.repo)
        return fetch_repo_data(owner=self.owner, repo=self.repo)

    def format_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return _format_repository_data(data, self.owner, self.repo)

    def display_data(
        self, formatted_data: Dict[str, Any], raw_data: Dict[str, Any]
    ) -> None:
        counts_info = _get_repository_counts_info(raw_data)
        _display_repository_info(formatted_data, counts_info)
        _display_scores(raw_data)
