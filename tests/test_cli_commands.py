from typer.testing import CliRunner
from ai_model_catalog.cli import app

runner = CliRunner()


def test_models_command_smoke():
    result = runner.invoke(
        app, ["models", "--owner", "huggingface", "--repo", "transformers"]
    )
    assert result.exit_code == 0
    assert "Stars:" in result.output


def test_hf_model_command_smoke():
    result = runner.invoke(app, ["hf_model", "--model-id", "bert-base-uncased"])
    assert result.exit_code == 0
    assert "Model:" in result.output


def test_invalid_command():
    result = runner.invoke(app, ["invalid_command"])
    assert result.exit_code != 0
    assert "Usage:" in result.output
