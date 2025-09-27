import json
from typing import Optional, Dict, Any

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


def safe_float(val: Any) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def safe_int(val: Any) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def build_ndjson_line(
    name: str,
    category: str,
    scores: Dict[str, Any],
    size_score_key: str = "size_score",
) -> Dict[str, Any]:
    size_score = scores.get(size_score_key, scores.get("size", {}))
    if not isinstance(size_score, dict):
        size_score = {}

    return {
        "name": name,
        "category": category,
        "net_score": safe_float(scores.get("net_score")),
        "net_score_latency": safe_int(scores.get("net_score_latency")),
        "ramp_up_time": safe_float(scores.get("ramp_up_time")),
        "ramp_up_time_latency": safe_int(scores.get("ramp_up_time_latency")),
        "bus_factor": safe_float(scores.get("bus_factor")),
        "bus_factor_latency": safe_int(scores.get("bus_factor_latency")),
        "performance_claims": safe_float(scores.get("performance_claims")),
        "performance_claims_latency": safe_int(scores.get("performance_claims_latency")),
        "license": safe_float(scores.get("license")),
        "license_latency": safe_int(scores.get("license_latency")),
        "size_score": size_score,
        "size_score_latency": safe_int(scores.get("size_score_latency", scores.get("size_latency", 0))),
        "dataset_and_code_score": safe_float(
            scores.get("dataset_and_code_score", scores.get("availability", 0.0))
        ),
        "dataset_and_code_score_latency": safe_int(
            scores.get("dataset_and_code_score_latency", scores.get("availability_latency", 0))
        ),
        "dataset_quality": safe_float(scores.get("dataset_quality")),
        "dataset_quality_latency": safe_int(scores.get("dataset_quality_latency")),
        "code_quality": safe_float(scores.get("code_quality")),
        "code_quality_latency": safe_int(scores.get("code_quality_latency")),
    }


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
        scores = score_repo_from_owner_and_repo(owner, repo)
        line = build_ndjson_line(raw.get("full_name") or f"{owner}/{repo}", "REPOSITORY", scores)
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
        scores = score_model_from_id(model_id)
        line = build_ndjson_line(model_id, "MODEL", scores)
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
        scores = score_dataset_from_id(dataset_id)
        line = build_ndjson_line(dataset_id, "DATASET", scores)
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
def multiple_urls():
    """Fetch and output NDJSON metadata from multiple GitHub repositories."""
    configure_logging()
    with open("URL_FILE.txt", "r", encoding="utf-8") as f:
        repos = [line.strip() for line in f if line.strip()]

    for repo_url in repos:
        if repo_url.endswith("/"):
            repo_url = repo_url[:-1]

        # More robust parsing: find 'github.com' and extract owner/repo after that
        if "github.com" not in repo_url:
            typer.echo(f"Invalid URL (no github.com): {repo_url}", err=True)
            continue

        try:
            # Parse URL path after github.com
            path = repo_url.split("github.com", 1)[1].strip("/")
            parts = path.split("/")
            if len(parts) < 2:
                typer.echo(f"Invalid URL (missing owner/repo): {repo_url}", err=True)
                continue
            owner = parts[0]
            repo = parts[1]
        except (ValueError, IndexError) as e:
            typer.echo(f"Error parsing URL: {repo_url} - {e}", err=True)
            continue

        handler = RepositoryHandler(owner, repo)
        raw = handler.fetch_data()
        scores = score_repo_from_owner_and_repo(owner, repo)

        line = build_ndjson_line(raw.get("full_name") or f"{owner}/{repo}", "REPOSITORY", scores)
        typer.echo(json.dumps(line))


@app.command()
def interactive():
    interactive_main()


if __name__ == "__main__":
    app()
