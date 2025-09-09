import logging
import typer
import requests

app = typer.Typer(help="AI/ML model catalog CLI")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("catalog")

@app.command()
def models(owner: str = "huggingface", repo: str = "transformers"):
    """
    Example: fetch metadata from GitHub API.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    log.info("Repo: %s ⭐ %s", data["full_name"], data["stargazers_count"])
    typer.echo(data.get("description", ""))

if __name__ == "__main__":
    app()
