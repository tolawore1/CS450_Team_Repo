import pytest
from typer.testing import CliRunner

from ai_model_catalog.cli import app

runner = CliRunner()


def test_models_command_smoke(monkeypatch):
    pytest.skip("Skipping due to GitHub API rate limits")

    def mock_fetch_repo_data(owner, repo):
        return {
            "full_name": f"{owner}/{repo}",
            "stars": 1000,
            "forks": 200,
            "open_issues": 5,
            "license": {"spdx_id": "mit"},
            "updated_at": "2024-01-01T00:00:00Z",
            "readme": "Mocked readme",
            "description": "Test repository",
            "default_branch": "main",
            "language": "Python",
            "size": 1024,
            "commits_count": 100,
            "contributors_count": 10,
            "issues_count": 5,
            "pulls_count": 3,
            "actions_count": 2,
            "commits": [],
            "contributors": [],
            "issues": [],
            "pulls": [],
            "actions": [],
        }

    monkeypatch.setattr(
        "ai_model_catalog.fetch_repo.fetch_repo_data", mock_fetch_repo_data
    )

    result = runner.invoke(
        app, ["models", "--owner", "huggingface", "--repo", "transformers"]
    )
    assert result.exit_code == 0
    assert "Repo:" in result.output


def test_hf_model_command_smoke(monkeypatch):
    # What ModelHandler ultimately calls:
    monkeypatch.setattr(
        "ai_model_catalog.fetch_repo.fetch_model_data",
        lambda mid: {
            "modelSize": 123,
            "license": "mit",
            "author": "tester",
            "readme": "# readme",
            "cardData": {},
            "downloads": 42,
            "lastModified": "2024-01-01",
        },
        raising=True,
    )

    # Use defaults (no option spelling needed)
    result = runner.invoke(app, ["hf-model"])
    assert result.exit_code == 0
    assert "Model:" in result.output


def test_invalid_command():
    result = runner.invoke(app, ["invalid_command"])
    assert result.exit_code != 0
    assert "Usage:" in result.output
