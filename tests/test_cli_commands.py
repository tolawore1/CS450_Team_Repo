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
    """
    `hf_model` should print JSON for an HF model id.
    We monkeypatch the shared fetch layer to avoid network.
    """

    def mock_fetch_model_data(model_id: str):
        return {
            "modelId": model_id,
            "author": "tester",
            "license": "mit",
            "downloads": 123,
            "lastModified": "2024-01-01",
            "readme": True,
            "cardData": {"tags": ["nlp", "bert"], "language": "en"},
        }

    monkeypatch.setattr(
        "ai_model_catalog.fetch_repo.fetch_model_data",
        mock_fetch_model_data,
        raising=True,
    )

    result = runner.invoke(app, ["hf_model", "--model-id", "bert-base-uncased"])
    assert result.exit_code == 0, result.stdout

    data = json.loads(result.stdout)
    assert data["source"] == "huggingface"
    assert data.get("downloads") == 123
    assert data.get("id") == "bert-base-uncased"
