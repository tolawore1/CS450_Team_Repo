import logging
import requests
import typer
from ai_model_catalog.metrics.score_model import netScore

app = typer.Typer(help="AI/ML model catalog CLI")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("catalog")

# --- GitHub repo command ---
@app.command()
def models(owner: str = "huggingface", repo: str = "transformers"):
    """Fetch metadata from GitHub API for a repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    log.info("Repo: %s ⭐ %s", data["full_name"], data["stargazers_count"])
    typer.echo(data.get("description", ""))
    scores = netScore(data)
    typer.echo("\nNetScore Breakdown:")
    for k, v in scores.items():
        typer.echo(f"{k}: {v}")

# --- Hugging Face model command ---
@app.command()
def hf_model(model_id: str = "bert-base-uncased"):
    """Fetch metadata from Hugging Face Hub for a given model ID."""
    url = f"https://huggingface.co/api/models/{model_id}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

    typer.echo(f"Model: {data['modelId']}")
    typer.echo(f"Last Modified: {data['lastModified']}")
    typer.echo(f"Downloads: {data.get('downloads', 'N/A')}")
    typer.echo(f"Tags: {', '.join(data.get('tags', []))}")
    if "pipeline_tag" in data:
        typer.echo(f"Task: {data['pipeline_tag']}")
        
    scores = netScore(data)
    typer.echo("\nNetScore Breakdown:")
    for k, v in scores.items():
        typer.echo(f"{k}: {v}")

if __name__ == "__main__":
    app(prog_name="cli.py")
