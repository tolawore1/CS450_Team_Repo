"""
Repository fetching functions for AI Model Catalog
"""
import logging
import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("catalog")

def models(owner: str = "huggingface", repo: str = "transformers"):
    """Fetch metadata from GitHub API for a repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    log.info(data)
    return data

def hf_model(model_id: str = "bert-base-uncased"):
    """Fetch metadata from Hugging Face Hub for a given model ID."""
    url = f"https://huggingface.co/api/models/{model_id}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

    log.info(data)
    return data
