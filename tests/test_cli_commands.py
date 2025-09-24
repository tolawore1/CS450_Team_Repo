import json
from typer.testing import CliRunner

from ai_model_catalog.cli import app

runner = CliRunner()


def test_models_command_smoke(monkeypatch):
    """
    `models` should print JSON for a GitHub repo.
    We monkeypatch the shared fetch layer to avoid network.
    """

    def mock_fetch_repo_data(owner: str, repo: str):
        # Values chosen to be JSON-safe; handlers may coerce types further
        return {
            "id": f"{owner}/{repo}",
            "owner": owner,
            "name": repo,
            "license": "mit",
            "downloads": 42,  # ints are fine
            "commits_count": 100,  # ints are fine
            "readme": True,  # handlers convert to has_readme
            "last_modified": "2024-01-01",
            "description": "Mocked repo",
        }

    monkeypatch.setattr(
        "ai_model_catalog.fetch_repo.fetch_repo_data",
        mock_fetch_repo_data,
        raising=True,
    )

    result = runner.invoke(
        app, ["models", "--owner", "huggingface", "--repo", "transformers"]
    )
    assert result.exit_code == 0, result.stdout

    # The command prints JSON; parse and validate key fields
    data = json.loads(result.stdout)
    assert data["source"] == "github"
    assert data.get("downloads") == 42
    assert data.get("commits_count") == 100
    assert "full_name" in data or "id" in data


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
