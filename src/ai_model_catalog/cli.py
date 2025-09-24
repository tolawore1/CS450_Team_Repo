import json
import time
from typing import Optional

import typer

from .fetch_repo import fetch_dataset_data
from .interactive import interactive_main
from .logging_config import configure_logging
from .model_sources.github_model import RepositoryHandler
from .model_sources.hf_model import ModelHandler
from .score_model import (
    score_dataset_from_id,
    score_model_from_id,
    score_repo_from_owner_and_repo,
)

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
        # Measure scoring time
        start_time = time.time()
        scores = score_repo_from_owner_and_repo(owner, repo)
        scoring_time = round((time.time() - start_time) * 1000)

        # Create simplified NDJSON output with total latency only
        line = {
            "name": raw.get("full_name") or f"{owner}/{repo}",
            "category": "REPOSITORY",
            "net_score": scores.get("NetScore", 0.0),
            "ramp_up_time": scores.get("ramp_up_time", 0.0),
            "bus_factor": scores.get("bus_factor", 0.0),
            "performance_claims": scores.get("performance_claims", 0.0),
            "license": scores.get("license", 0.0),
            "size_score": scores.get("size", {}),
            "dataset_and_code_score": scores.get("availability", 0.0),
            "dataset_quality": scores.get("dataset_quality", 0.0),
            "code_quality": scores.get("code_quality", 0.0),
            "latency": scoring_time,
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
        # Measure scoring time
        start_time = time.time()
        scores = score_model_from_id(model_id)
        scoring_time = round((time.time() - start_time) * 1000)

        # Create simplified NDJSON output with total latency only
        line = {
            "name": model_id,
            "category": "MODEL",
            "net_score": scores.get("NetScore", 0.0),
            "ramp_up_time": scores.get("ramp_up_time", 0.0),
            "bus_factor": scores.get("bus_factor", 0.0),
            "performance_claims": scores.get("performance_claims", 0.0),
            "license": scores.get("license", 0.0),
            "size_score": scores.get("size", {}),
            "dataset_and_code_score": scores.get("availability", 0.0),
            "dataset_quality": scores.get("dataset_quality", 0.0),
            "code_quality": scores.get("code_quality", 0.0),
            "latency": scoring_time,
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
        # Measure scoring time
        start_time = time.time()
        scores = score_dataset_from_id(dataset_id)
        scoring_time = round((time.time() - start_time) * 1000)

        # Create simplified NDJSON output with total latency only
        line = {
            "name": dataset_id,
            "category": "DATASET",
            "net_score": scores.get("NetScore", 0.0),
            "ramp_up_time": scores.get("ramp_up_time", 0.0),
            "bus_factor": scores.get("bus_factor", 0.0),
            "performance_claims": scores.get("performance_claims", 0.0),
            "license": scores.get("license", 0.0),
            "size_score": scores.get("size", {}),
            "dataset_and_code_score": scores.get("availability", 0.0),
            "dataset_quality": scores.get("dataset_quality", 0.0),
            "code_quality": scores.get("code_quality", 0.0),
            "latency": scoring_time,
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
