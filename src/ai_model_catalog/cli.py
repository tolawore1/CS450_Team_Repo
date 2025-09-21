import typer
from ai_model_catalog.model_sources.github_model import RepositoryHandler
from ai_model_catalog.model_sources.hf_model import ModelHandler
from ai_model_catalog.interactive import interactive_main

app = typer.Typer()


@app.command()
def models(owner: str = "huggingface", repo: str = "transformers"):
    """Fetch metadata from GitHub API for a repo."""
    handler = RepositoryHandler(owner, repo)
    handler.fetch_data()


@app.command()
def hf_model(model_id: str = "bert-base-uncased"):
    """Fetch metadata from Hugging Face Hub for a given model ID."""
    handler = ModelHandler(model_id)
    handler.fetch_data()


@app.command()
def interactive():
    """Start interactive mode for browsing AI models."""
    interactive_main()


if __name__ == "__main__":
    app()
