from typer.testing import CliRunner

from ai_model_catalog.cli import app

runner = CliRunner()


def test_models_command_smoke():
    result = runner.invoke(
        app, ["models", "--owner", "huggingface", "--repo", "transformers"]
    )
    assert result.exit_code == 0
    assert "Stars:" in result.output


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
