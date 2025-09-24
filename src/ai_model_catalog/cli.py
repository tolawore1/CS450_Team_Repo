import json
from typing import Optional

import typer

from .fetch_repo import fetch_dataset_data
from .interactive import interactive_main
from .logging_config import configure_logging
from .model_sources.github_model import RepositoryHandler
from .model_sources.hf_model import ModelHandler

app = typer.Typer()


@app.command()
def models(
    owner: str = "huggingface",
    repo: str = "transformers",
    output_format: Optional[str] = typer.Option(
        "text", "--format", help="Output format (text or ndjson)"
    ),
):
    """Fetch and display metadata from GitHub API for a repository."""
    configure_logging()
    handler = RepositoryHandler(owner, repo)
    raw = handler.fetch_data()

    if output_format == "ndjson":
        # For repos, output summary as ndjson
        line = {
            "full_name": raw.get("full_name") or f"{owner}/{repo}",
            "stars": raw.get("stars", 0),
            "forks": raw.get("forks", 0),
            "open_issues": raw.get("open_issues", 0),
            "license": raw.get("license"),
            "updated_at": raw.get("updated_at") or raw.get("pushed_at"),
        }
        typer.echo(json.dumps(line))
        return

    formatted = handler.format_data(raw)
    handler.display_data(formatted, raw)


@app.command(name="hf-model")
def hf_model(
    model_id: str = "bert-base-uncased",
    output_format: Optional[str] = typer.Option(
        "text", "--format", help="Output format (text or ndjson)"
    ),
):
    """Fetch and display metadata from Hugging Face Hub for a model."""
    configure_logging()
    handler = ModelHandler(model_id)
    raw = handler.fetch_data()

    if output_format == "ndjson":
        line = {
            "model_id": model_id,
            "model_size": raw.get("modelSize", 0),
            "downloads": raw.get("downloads", 0),
            "license": raw.get("license"),
            "last_modified": raw.get("lastModified", ""),
        }
        typer.echo(json.dumps(line))
        return

    formatted = handler.format_data(raw)
    handler.display_data(formatted, raw)


@app.command(name="hf-dataset")
def hf_dataset(
    dataset_id: str = "imdb",
    output_format: Optional[str] = typer.Option(
        "text", "--format", help="Output format (text or ndjson)"
    ),
):
    """Fetch and display metadata from Hugging Face Hub for a dataset."""
    configure_logging()
    raw = fetch_dataset_data(dataset_id)

    if output_format == "ndjson":
        line = {
            "dataset_id": dataset_id,
            "downloads": raw.get("downloads", 0),
            "license": raw.get("license"),
            "last_modified": raw.get("lastModified", ""),
            "task_categories": raw.get("taskCategories", []),
        }
        typer.echo(json.dumps(line))
        return

    # text output
    typer.echo(f"Dataset: {dataset_id}")
    typer.echo(f"Author: {raw.get('author') or 'Unknown'}")
    typer.echo(f"License: {raw.get('license')}")
    typer.echo(f"Downloads: {raw.get('downloads', 0)}")
    typer.echo(f"Last Modified: {raw.get('lastModified', '')}")
    tags = raw.get("tags") or []
    if tags:
        typer.echo(f"Tags: {', '.join(tags)}")
    tcats = raw.get("taskCategories") or []
    if tcats:
        typer.echo(f"Task Categories: {', '.join(map(str, tcats))}")


@app.command()
def interactive():
    """Start interactive mode for browsing AI models."""
    interactive_main()


if __name__ == "__main__":
    app()
