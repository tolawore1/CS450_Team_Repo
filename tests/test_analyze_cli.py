from pathlib import Path
import json
from typer.testing import CliRunner

from ai_model_catalog.cli import app

runner = CliRunner()


def test_analyze_local_cli(tmp_path: Path):
    """analyze should accept a local path and return JSON with source=local."""
    # make the directory "look like" a repo (README presence is enough for our scan)
    (tmp_path / "README.md").write_text("# demo\n")

    result = runner.invoke(app, ["analyze", str(tmp_path), "-f", "json"])
    assert result.exit_code == 0, result.stdout

    data = json.loads(result.stdout)
    assert data["source"] == "local"
    assert data["has_readme"] is True
    # sanity checks that the scanner actually walked the directory
    assert data["file_count"] >= 1
    assert data["size_bytes"] >= 1


def test_analyze_github_url_cli(monkeypatch):
    """analyze should accept a GitHub URL when fetch is monkeypatched."""

    # --- mock the shared fetch function used by RepositoryHandler ---
    def mock_fetch_repo_data(owner: str, repo: str):
        # Keep it simple and JSON-friendly; handlers will normalize this
        return {
            "id": f"{owner}/{repo}",
            "owner": owner,
            "name": repo,
            "license": "mit",
            "downloads": 42,
            "commits_count": 100,
            "readme": True,
            "last_modified": "2024-01-01T00:00:00Z",
            "description": "Mocked repo for tests",
        }

    monkeypatch.setattr(
        "ai_model_catalog.fetch_repo.fetch_repo_data",
        mock_fetch_repo_data,
        raising=True,
    )

    url = "https://github.com/huggingface/transformers"
    result = runner.invoke(app, ["analyze", url, "-f", "json"])
    assert result.exit_code == 0, result.stdout

    data = json.loads(result.stdout)
    assert data["source"] == "github"
    assert data.get("downloads") == 42
    assert data.get("commits_count") == 100
    assert data.get("has_readme") in (True, False)  # tolerant to formatter choice
