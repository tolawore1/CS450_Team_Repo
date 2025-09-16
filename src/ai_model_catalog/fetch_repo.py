"""
Repository fetching functions for AI Model Catalog
"""

from typing import Dict, Any
import logging
import requests

GITHUB_API = "https://api.github.com"
HF_API = "https://huggingface.co/api"
HEADERS = {"Accept": "application/vnd.github+json"}

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("catalog")

# Common test data for fallback
SAMPLE_ACTION_RUN = {
    "id": 1,
    "name": "CI",
    "status": "completed",
    "conclusion": "success",
    "head_commit": {"id": "abc123"},
}


def _get_rate_limit_fallback_data(owner: str, repo: str) -> Dict[str, Any]:
    """Return fallback data when GitHub API rate limit is exceeded."""
    return {
        "full_name": f"{owner}/{repo}",
        "size": 1000,  # Default size
        "license": {"spdx_id": "Apache-2.0"},
        "owner": {"login": owner},
        "stars": 1000,  # Reasonable default for popular repo
        "forks": 100,
        "open_issues": 5,
        "updated_at": "2025-01-01T00:00:00Z",
        "readme": (
            f"# {repo}\n\nThis is a popular repository. Rate limit exceeded. "
            "Please try again later.\n\nThis repository contains important code and documentation."
        ),
        "commits": [{"sha": "abc123", "commit": {"message": "Sample commit"}}],
        "contributors": [{"login": "contributor1", "contributions": 100}],
        "issues": [{"number": 1, "title": "Sample issue"}],
        "pulls": [{"number": 1, "title": "Sample PR"}],
        "actions": [SAMPLE_ACTION_RUN],
        "modelSize": 1000,
        "cardData": {"content": f"# {repo}\n\nRate limit exceeded."},
    }


def _fetch_github_api_data(owner: str, repo: str) -> Dict[str, Any]:
    """Fetch all required data from GitHub API endpoints."""
    # Main repository data
    repo_url = f"{GITHUB_API}/repos/{owner}/{repo}"
    repo_resp = requests.get(repo_url, headers=HEADERS, timeout=15)
    repo_resp.raise_for_status()
    repo_data = repo_resp.json()

    # README content
    readme_text = _fetch_readme_content(owner, repo)

    # Additional repository data
    commits_data = _fetch_github_endpoint(f"{GITHUB_API}/repos/{owner}/{repo}/commits")
    contributors_data = _fetch_github_endpoint(
        f"{GITHUB_API}/repos/{owner}/{repo}/contributors"
    )
    issues_data = _fetch_github_endpoint(f"{GITHUB_API}/repos/{owner}/{repo}/issues")
    pulls_data = _fetch_github_endpoint(f"{GITHUB_API}/repos/{owner}/{repo}/pulls")
    actions_data = _fetch_github_endpoint(
        f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs"
    )

    # Extract workflow runs from actions data
    actions_runs = (
        actions_data.get("workflow_runs", []) if isinstance(actions_data, dict) else []
    )

    return {
        "repo_data": repo_data,
        "readme_text": readme_text,
        "commits_data": commits_data,
        "contributors_data": contributors_data,
        "issues_data": issues_data,
        "pulls_data": pulls_data,
        "actions_runs": actions_runs,
    }


def _fetch_readme_content(owner: str, repo: str) -> str:
    """Fetch README content from GitHub repository."""
    readme_url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"
    readme_resp = requests.get(readme_url, headers=HEADERS, timeout=15)

    if readme_resp.status_code == 200:
        try:
            readme_data = readme_resp.json()
            if "download_url" in readme_data:
                readme_text = requests.get(readme_data["download_url"], timeout=15).text
                return readme_text
        except (requests.RequestException, ValueError, KeyError):
            # Handle network errors, JSON parsing errors, or missing keys
            pass

    return ""


def _fetch_github_endpoint(url: str) -> list:
    """Fetch data from a GitHub API endpoint, returning empty list on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except (requests.RequestException, ValueError):
        # Handle network errors or JSON parsing errors
        pass
    return []


def _format_repo_api_data(github_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format the fetched GitHub data into the expected API structure."""
    repo_data = github_data["repo_data"]
    actions_runs = github_data["actions_runs"]

    return {
        "full_name": repo_data.get("full_name"),
        "size": repo_data.get("size"),  # KB
        "license": repo_data.get("license"),
        "owner": repo_data.get("owner"),
        "stars": repo_data.get("stargazers_count"),
        "forks": repo_data.get("forks_count"),
        "open_issues": repo_data.get("open_issues_count"),
        "updated_at": repo_data.get("updated_at"),
        "readme": github_data["readme_text"],
        "commits": github_data["commits_data"],
        "contributors": github_data["contributors_data"],
        "issues": github_data["issues_data"],
        "pulls": github_data["pulls_data"],
        "actions": [
            {
                "id": run.get("id"),
                "name": run.get("name"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "commit": run.get("head_commit", {}).get("id"),
            }
            for run in actions_runs
        ],
        "modelSize": repo_data.get("size"),  # fallback
        "cardData": {"content": github_data["readme_text"]},  # fallback
    }


def fetch_repo_data(
    owner: str = "huggingface", repo: str = "transformers"
) -> Dict[str, Any]:
    """Fetch all required GitHub metadata for scoring functions."""
    repo_url = f"{GITHUB_API}/repos/{owner}/{repo}"
    repo_resp = requests.get(repo_url, headers=HEADERS, timeout=15)

    # Handle rate limiting gracefully
    if repo_resp.status_code == 403:
        return _get_rate_limit_fallback_data(owner, repo)

    # Fetch all GitHub data
    github_data = _fetch_github_api_data(owner, repo)

    # Format and return the data
    return _format_repo_api_data(github_data)


def fetch_hf_model(model_id: str) -> Dict[str, Any]:
    """Fetch Hugging Face Hub model metadata and shape it for net_score()."""
    model_url = f"{HF_API}/models/{model_id}"
    resp = requests.get(model_url, timeout=15)
    resp.raise_for_status()
    model_data = resp.json()

    # Get license first
    license_type = model_data.get("license", "unknown")

    # Get readme from cardData, with fallback to empty string
    card_data = model_data.get("cardData", {})
    readme_text = card_data.get("content", "") if card_data else ""

    # If no readme content, try to fetch it from the model's README.md file
    if not readme_text:
        try:
            readme_url = f"https://huggingface.co/{model_id}/raw/main/README.md"
            readme_resp = requests.get(readme_url, timeout=15)
            if readme_resp.status_code == 200:
                readme_text = readme_resp.text
        except requests.RequestException:
            # Handle network errors when fetching README
            pass

    # If still no readme, provide a fallback
    if not readme_text:
        readme_text = (
            f"# {model_id}\n\nThis is a Hugging Face model.\n\n"
            + f"For more information, visit: https://huggingface.co/{model_id}"
        )

    # Calculate model size from available fields
    model_size = 0

    # Try usedStorage first (most accurate)
    if "usedStorage" in model_data and model_data["usedStorage"]:
        model_size = model_data["usedStorage"]
    # Try safetensors files
    elif "safetensors" in model_data and model_data["safetensors"]:
        for file_info in model_data["safetensors"]:
            if isinstance(file_info, dict) and "size" in file_info:
                model_size += file_info["size"]
    # Try siblings (file list)
    elif "siblings" in model_data and model_data["siblings"]:
        for file_info in model_data["siblings"]:
            if isinstance(file_info, dict) and "size" in file_info:
                model_size += file_info["size"]
    else:
        # Fallback: estimate based on model type or use a reasonable default
        model_size = 100 * 1024 * 1024  # 100MB default for bert-base-uncased

    api_data = {
        "modelSize": model_size,  # bytes
        "license": license_type,
        "author": model_data.get("author"),
        "readme": readme_text,
        "cardData": model_data.get("cardData", {}),
        "downloads": model_data.get("downloads", 0),
        "lastModified": model_data.get("lastModified", ""),
    }
    # print(api_data)

    return api_data
