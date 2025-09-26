import logging
from typing import Dict

from .fetch_repo import fetch_dataset_data, fetch_model_data, fetch_repo_data
from .metrics.score_available_dataset_and_code import (
    score_available_dataset_and_code as score_availability,
)
from .metrics.score_bus_factor import score_bus_factor
from .metrics.score_code_quality import score_code_quality
from .metrics.score_dataset_quality import score_dataset_quality
from .metrics.score_license import score_license
from .metrics.score_performance_claims import score_performance_claims
from .metrics.score_ramp_up_time import score_ramp_up_time
from .metrics.score_size import score_size

log = logging.getLogger(__name__)


def _ensure_size_score_structure(size_scores):
    """Ensure size_scores is always a dictionary with proper structure."""
    if not isinstance(size_scores, dict):
        size_scores = {
            "raspberry_pi": 0.0,
            "jetson_nano": 0.0,
            "desktop_pc": 0.0,
            "aws_server": 0.0,
        }

    # Ensure all hardware keys are present
    for hardware in ["raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"]:
        if hardware not in size_scores:
            size_scores[hardware] = 0.0
        # Ensure the value is a float, not boolean
        size_scores[hardware] = float(size_scores[hardware])

    return size_scores


def net_score(api_data: Dict) -> Dict[str, float]:
    log.debug("net_score: input keys=%s", list(api_data.keys()))

    repo_size_bytes = (
        api_data.get("size", 0) * 1024
        if "full_name" in api_data
        else api_data.get("modelSize", 0)
    )
    license_type = (
        api_data.get("license", {}).get("spdx_id")
        if isinstance(api_data.get("license"), dict)
        else api_data.get("license")
    )
    readme = api_data.get("readme", "") or api_data.get("cardData", {}).get(
        "content", ""
    )
    maintainers = (
        [api_data.get("owner", {}).get("login")]
        if "owner" in api_data
        else [api_data.get("author")]
    )

    model_data = {
        "repo_size_bytes": repo_size_bytes,
        "license": license_type,
        "readme": readme,
        "maintainers": maintainers,
        "has_code": api_data.get("has_code", True),
        "has_dataset": api_data.get("has_dataset", True),
    }

    # Get size scores (now returns object with hardware mappings)
    size_scores = score_size(model_data["repo_size_bytes"])

    # Calculate weighted average of hardware scores for net score
    # Weight more capable hardware more heavily
    hardware_weights = {
        "raspberry_pi": 0.1,  # Least capable
        "jetson_nano": 0.2,  # More capable
        "desktop_pc": 0.3,  # Most common
        "aws_server": 0.4,  # Most capable
    }
    size_score_avg = sum(
        size_scores[hw] * weight for hw, weight in hardware_weights.items()
    )

    # Ensure size_scores is always a dictionary with proper structure
    size_scores = _ensure_size_score_structure(size_scores)

    scores = {
        "size": size_scores,  # Keep the full object for NDJSON output
        "size_score": size_score_avg,  # Single float for net score calculation
        "license": max(0.0, min(1.0, score_license(model_data))),
        "ramp_up_time": max(0.0, min(1.0, score_ramp_up_time(model_data["readme"]))),
        "bus_factor": max(0.0, min(1.0, score_bus_factor(model_data["maintainers"]))),
        "availability": max(
            0.0,
            min(
                1.0,
                score_availability(model_data["has_code"], model_data["has_dataset"]),
            ),
        ),
        "dataset_quality": max(0.0, min(1.0, score_dataset_quality(api_data))),
        "code_quality": max(0.0, min(1.0, score_code_quality(api_data))),
        "performance_claims": max(0.0, min(1.0, score_performance_claims(model_data))),
    }

    weights = {
        "size_score": 0.1,  # Use the averaged size score for net calculation
        "license": 0.15,
        "ramp_up_time": 0.15,
        "bus_factor": 0.1,
        "availability": 0.1,
        "dataset_quality": 0.1,
        "code_quality": 0.15,
        "performance_claims": 0.15,
    }

    netscore = sum(scores[k] * weights[k] for k in weights)
    scores["NetScore"] = round(netscore, 3)
    log.debug("component scores=%s", scores)
    log.info("NetScore=%s", scores["NetScore"])
    return scores


def score_model_from_id(model_id: str) -> Dict[str, float]:
    api_data = fetch_model_data(model_id)
    return net_score(api_data)


def score_repo_from_owner_and_repo(owner: str, repo: str) -> Dict[str, float]:
    log.info("Scoring repository %s/%s", owner, repo)
    api_data = fetch_repo_data(owner=owner, repo=repo)
    return net_score(api_data)


def score_dataset_from_id(dataset_id: str) -> Dict[str, float]:
    """Score a Hugging Face dataset using available metrics."""
    api_data = fetch_dataset_data(dataset_id)

    # Create model_data structure for scoring
    model_data = {
        "repo_size_bytes": 0,  # Datasets don't have size in same way
        "license": api_data.get("license"),
        "readme": api_data.get("readme", ""),
        "maintainers": [api_data.get("author")],
        "has_code": False,  # Datasets typically don't have code
        "has_dataset": True,  # It is a dataset
    }

    # Get size scores (minimal for datasets)
    size_scores = {
        "raspberry_pi": 0.5,
        "jetson_nano": 0.5,
        "desktop_pc": 0.5,
        "aws_server": 0.5,
    }

    scores = {
        "size": size_scores,
        "size_score": 0.5,  # Neutral score for datasets
        "license": max(0.0, min(1.0, score_license(model_data))),
        "ramp_up_time": max(0.0, min(1.0, score_ramp_up_time(model_data["readme"]))),
        "bus_factor": max(0.0, min(1.0, score_bus_factor(model_data["maintainers"]))),
        "availability": max(
            0.0,
            min(
                1.0,
                score_availability(model_data["has_code"], model_data["has_dataset"]),
            ),
        ),
        "dataset_quality": max(0.0, min(1.0, score_dataset_quality(api_data))),
        "code_quality": 0.0,  # Datasets don't have code quality
        "performance_claims": max(0.0, min(1.0, score_performance_claims(model_data))),
    }

    # Calculate NetScore
    weights = {
        "size_score": 0.1,
        "license": 0.15,
        "ramp_up_time": 0.15,
        "bus_factor": 0.1,
        "availability": 0.1,
        "dataset_quality": 0.2,  # Higher weight for dataset quality
        "code_quality": 0.0,  # No weight for code quality
        "performance_claims": 0.2,  # Higher weight for performance claims
    }

    netscore = sum(scores[k] * weights[k] for k in weights if weights[k] > 0)
    scores["NetScore"] = round(netscore, 3)

    return scores
