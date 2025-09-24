# --- stdlib ---
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

# --- third-party ---
import typer

try:
    from git import Repo  # Optional: GitPython for richer local git metadata
except Exception:
    Repo = None  # type: ignore

# --- local ---
from ai_model_catalog.interactive import interactive_main
from ai_model_catalog.logging_config import configure_logging
from ai_model_catalog.model_sources.github_model import RepositoryHandler
from ai_model_catalog.model_sources.hf_model import ModelHandler
from ai_model_catalog.score_model import net_score

app = typer.Typer(help="AI/ML model catalog CLI")  # << single app only >>

# --------------------------------
# Helpers
# --------------------------------
_GITHUB_RE = re.compile(r"(?:https?://)?github\.com/([^/\s]+)/([^/\s#?]+)")


def _detect_source(s: str):
    """Classify input as GitHub repo, local path, or unknown."""
    s = s.strip()
    m = _GITHUB_RE.search(s)
    if m:
        owner, repo = m.groups()
        return "github", {"owner": owner, "repo": repo}
    p = Path(s).expanduser()
    if p.exists():
        return "local", {"path": str(p.resolve())}
    return "unknown", {"value": s}


def _scan_local_repo(path: Path) -> Dict[str, Any]:
    """Local repository analysis using GitPython when available, with a safe fallback."""
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(str(path))

    data: Dict[str, Any] = {
        "source": "local",
        "root": str(path),
        "has_readme": False,
        "readme": "",
        "license_file": "",
        "file_count": 0,
        "py_files": 0,
        "test_files": 0,
        "size_bytes": 0,
        "is_git": False,
        "branch": "",
        "last_commit": "",  # "<sha> <unix_ts>"
        "contributors": [],  # [{"id": email/name, "commits": N}, ...]
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
        except Exception:
            pass  # not a git repo or GitPython unavailable

    # Filesystem scan (skip heavy dirs)
    SKIP = {
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
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            fp = Path(root) / f
            try:
                data["size_bytes"] += fp.stat().st_size
            except Exception:
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


# --------------------------------
# Commands (all on the SAME app)
# --------------------------------
@app.command(name="models")
def models(owner: str = "huggingface", repo: str = "transformers"):
    """Fetch and display metadata from GitHub API for a repository."""
    configure_logging()
    handler = RepositoryHandler(owner, repo)
    raw = handler.fetch_data()
    formatted = handler.format_data(raw)
    handler.display_data(formatted, raw)


@app.command(name="hf_model")  # keep underscore for tests
def hf_model(model_id: str = "bert-base-uncased"):
    """Fetch and display metadata from Hugging Face Hub for a model."""
    configure_logging()
    handler = ModelHandler(model_id)
    raw = handler.fetch_data()
    formatted = handler.format_data(raw)
    handler.display_data(formatted, raw)


@app.command(name="interactive")
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
                f"Error: could not determine source for {source!r}. Provide a GitHub URL or an existing local path.",
                err=True,
            )
            raise typer.Exit(2)

    # Optional score
    try:
        data["net_score"] = net_score(data)
    except Exception:
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
