import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

import typer

# Try to import GitPython, but make it optional
try:
    from git import Repo
except ImportError:
    Repo = None

from .fetch_repo import fetch_dataset_data
from .interactive import interactive_main
from .logging_config import configure_logging
from .model_sources.github_model import RepositoryHandler
from .model_sources.hf_model import ModelHandler
from .score_model import net_score

app = typer.Typer()


def _detect_source(source: str) -> Tuple[str, Dict]:
    """Detect if source is a GitHub URL or local path."""
    if source.startswith(("https://github.com/", "http://github.com/")):
        # Extract owner/repo from GitHub URL
        parts = source.rstrip("/").split("/")
        if len(parts) >= 5:
            owner = parts[-2]
            repo = parts[-1]
            return "github", {"owner": owner, "repo": repo}

    # Check if it's a local path
    path = Path(source).expanduser()
    if path.exists():
        return "local", {"path": str(path)}

    return "unknown", {}


def _scan_local_repo(path: Path) -> Dict:
    """Scan a local repository for metadata."""
    data = {
        "source": "local",
        "path": str(path),
        "size_bytes": 0,
        "file_count": 0,
        "py_files": 0,
        "test_files": 0,
        "has_readme": False,
        "readme": "",
        "license_file": "",
        "is_git": False,
        "branch": "",
        "last_commit": "",
        "contributors": [],
    }

    # Optional Git metadata
    if Repo is not None:
        try:
            repo = Repo(path, search_parent_directories=True)
            data["is_git"] = True
            data["branch"] = (
                repo.active_branch.name if not repo.head.is_detached else "(detached)"
            )
            commit = repo.head.commit
            data["last_commit"] = f"{commit.hexsha} {int(commit.committed_date)}"
            counts: Dict[str, int] = {}
            for c in repo.iter_commits(max_count=1000):
                email = c.author.email or c.author.name
                counts[email] = counts.get(email, 0) + 1
            data["contributors"] = sorted(
                ({"id": k, "commits": v} for k, v in counts.items()),
                key=lambda x: x["commits"],
                reverse=True,
            )[:10]
        except (OSError, ValueError, TypeError):
            pass  # not a git repo or GitPython unavailable

    # Filesystem scan (skip heavy dirs)
    skip_dirs = {
        ".git",
        ".venv",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        "node_modules",
        "dist",
        "build",
        ".dist",
    }

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            fp = Path(root) / f
            try:
                data["size_bytes"] += fp.stat().st_size
            except (OSError, PermissionError):
                pass
            data["file_count"] += 1
            low = f.lower()
            if low.endswith(".py"):
                data["py_files"] += 1
                if "test" in low or "tests" in str(fp.parent).lower():
                    data["test_files"] += 1
            if not data["has_readme"] and low in {
                "readme.md",
                "readme.rst",
                "readme.txt",
                "readme",
            }:
                data["has_readme"] = True
                data["readme"] = str(fp.relative_to(path))
            if not data["license_file"] and low in {
                "license",
                "license.md",
                "license.txt",
                "copying",
            }:
                data["license_file"] = str(fp.relative_to(path))

    return data


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
    handler.display_data(formatted)


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
    handler.display_data(formatted)


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


@app.command(name="analyze")
def analyze(
    source: str = typer.Argument(
        ..., help="GitHub URL like https://github.com/owner/repo or a local path '.'"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write JSON/NDJSON to file"
    ),
    fmt: str = typer.Option(
        "json", "--format", "-f", help="json|ndjson", case_sensitive=False
    ),
):
    """Analyze a repository from GitHub or a local directory."""
    configure_logging()
    kind, info = _detect_source(source)

    if kind == "github":
        handler = RepositoryHandler(info["owner"], info["repo"])
        raw = handler.fetch_data()
        data = handler.format_data(raw)
    elif kind == "local":
        data = _scan_local_repo(Path(info["path"]))
    else:
        # Fallback: treat as local path if it exists, otherwise usage error
        p = Path(source).expanduser()
        if p.exists():
            data = _scan_local_repo(p)
        else:
            typer.echo(
                f"Error: could not determine source for {source!r}. "
                "Provide a GitHub URL or an existing local path.",
                err=True,
            )
            raise typer.Exit(2)

    # Optional score
    try:
        data["net_score"] = net_score(data)
    except (KeyError, ValueError, TypeError):
        pass

    # Output
    if fmt.lower() == "ndjson":
        line = json.dumps(data, ensure_ascii=False)
        if output:
            output.write_text(line + "\n", encoding="utf-8")
        else:
            typer.echo(line)
    else:
        blob = json.dumps(data, indent=2, ensure_ascii=False)
        if output:
            output.write_text(blob + "\n", encoding="utf-8")
        else:
            typer.echo(blob)


if __name__ == "__main__":
    app()
