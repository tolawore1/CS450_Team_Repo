import typer

from ai_model_catalog.interactive import interactive_main
from ai_model_catalog.logging_config import configure_logging
from ai_model_catalog.model_sources.github_model import RepositoryHandler
from ai_model_catalog.model_sources.hf_model import ModelHandler

app = typer.Typer()


@app.command()
def models(owner: str = "huggingface", repo: str = "transformers"):
    """Fetch and display metadata from GitHub API for a repository."""
    configure_logging()
    handler = RepositoryHandler(owner, repo)
    raw = handler.fetch_data()
    formatted = handler.format_data(raw)
    handler.display_data(formatted, raw)


@app.command()
def hf_model(model_id: str = "bert-base-uncased"):
    """Fetch and display metadata from Hugging Face Hub for a model."""
    configure_logging()
    handler = ModelHandler(model_id)
    raw = handler.fetch_data()
    formatted = handler.format_data(raw)
    handler.display_data(formatted, raw)


@app.command()
def interactive():
    """Start interactive mode for browsing AI models."""
    interactive_main()


if __name__ == "__main__":
    app()
