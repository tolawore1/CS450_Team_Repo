import logging
from typing import Dict

from .fetch_repo import fetch_dataset_data, fetch_model_data, fetch_repo_data

# Import *_with_latency versions
from .metrics.score_available_dataset_and_code import score_available_dataset_and_code_with_latency
from .metrics.score_bus_factor import score_bus_factor_with_latency
from .metrics.score_code_quality import score_code_quality_with_latency
from .metrics.score_dataset_quality import score_dataset_quality_with_latency
from .metrics.score_license import score_license_with_latency
from .metrics.score_performance_claims import score_performance_claims_with_latency
from .metrics.score_ramp_up_time import score_ramp_up_time_with_latency
from .metrics.score_size import score_size_with_latency

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

    for hardware in ["raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"]:
        if hardware not in size_scores:
            size_scores[hardware] = 0.0
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
    readme = api_data.get("readme", "") or api_data.get("cardData", {}).get("content", "")
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

    # Call each metric with latency
    size_scores, size_latency = score_size_with_latency(model_data["repo_size_bytes"])
    size_scores = _ensure_size_score_structure(size_scores)

    license_score, license_latency = score_license_with_latency(model_data)
    ramp_up_score, ramp_up_latency = score_ramp_up_time_with_latency(model_data["readme"])
    bus_factor_score, bus_factor_latency = score_bus_factor_with_latency(model_data["maintainers"])
    availability_score, availability_latency = score_available_dataset_and_code_with_latency(
        model_data["has_code"], model_data["has_dataset"]
    )
    dataset_quality_score, dataset_quality_latency = score_dataset_quality_with_latency(api_data)
    code_quality_score, code_quality_latency = score_code_quality_with_latency(api_data)
    performance_claims_score, performance_claims_latency = score_performance_claims_with_latency(model_data)

    # Weighted average size score
    hardware_weights = {
        "raspberry_pi": 0.1,
        "jetson_nano": 0.2,
        "desktop_pc": 0.3,
        "aws_server": 0.4,
    }
    size_score_avg = sum(size_scores[hw] * weight for hw, weight in hardware_weights.items())

    # Combine all scores
    scores = {
        "size": size_scores,
        "size_score": size_score_avg,
        "size_score_latency": size_latency,

        "license": license_score,
        "license_latency": license_latency,

        "ramp_up_time": ramp_up_score,
        "ramp_up_time_latency": ramp_up_latency,

        "bus_factor": bus_factor_score,
        "bus_factor_latency": bus_factor_latency,

        "dataset_and_code_score": availability_score,
        "dataset_and_code_score_latency": availability_latency,

        "dataset_quality": dataset_quality_score,
        "dataset_quality_latency": dataset_quality_latency,

        "code_quality": code_quality_score,
        "code_quality_latency": code_quality_latency,

        "performance_claims": performance_claims_score,
        "performance_claims_latency": performance_claims_latency,
    }

    # NetScore weights
    weights = {
        "size_score": 0.1,
        "license": 0.15,
        "ramp_up_time": 0.15,
        "bus_factor": 0.1,
        "dataset_and_code_score": 0.1,
        "dataset_quality": 0.1,
        "code_quality": 0.15,
        "performance_claims": 0.15,
    }

    netscore = sum(scores[k] * weights[k] for k in weights)
    scores["net_score"] = round(netscore, 3)

    # Net latency is sum of all individual latencies
    scores["net_score_latency"] = (
        size_latency + license_latency + ramp_up_latency + bus_factor_latency +
        availability_latency + dataset_quality_latency + code_quality_latency +
        performance_claims_latency
    )

    log.debug("component scores=%s", scores)
    log.info("NetScore=%s", scores["net_score"])
    return scores


def score_model_from_id(model_id: str) -> Dict[str, float]:
    api_data = fetch_model_data(model_id)
    scores = net_score(api_data)

    def safe_score(val):
        try:
            return min(max(float(val), 0.0), 1.0)
        except:
            return 0.0

    def safe_latency(val):
        try:
            return max(int(val), 0)
        except:
            return 0

    def safe_size(size_dict):
        if not isinstance(size_dict, dict):
            return {"cpu": 0.0, "gpu": 0.0, "tpu": 0.0}
        return {
            "cpu": safe_score(size_dict.get("raspberry_pi", 0.0)),
            "gpu": safe_score(size_dict.get("jetson_nano", 0.0)),
            "tpu": safe_score(size_dict.get("aws_server", 0.0)),
        }

    return {
        "net_score": safe_score(scores.get("net_score")),
        "net_score_latency": safe_latency(scores.get("net_score_latency")),

        "ramp_up_time": safe_score(scores.get("ramp_up_time")),
        "ramp_up_time_latency": safe_latency(scores.get("ramp_up_time_latency")),

        "bus_factor": safe_score(scores.get("bus_factor")),
        "bus_factor_latency": safe_latency(scores.get("bus_factor_latency")),

        "performance_claims": safe_score(scores.get("performance_claims")),
        "performance_claims_latency": safe_latency(scores.get("performance_claims_latency")),

        "license": safe_score(scores.get("license")),
        "license_latency": safe_latency(scores.get("license_latency")),

        "size": safe_size(scores.get("size")),
        "size_latency": safe_latency(scores.get("size_score_latency")),

        "availability": safe_score(scores.get("dataset_and_code_score")),
        "availability_latency": safe_latency(scores.get("dataset_and_code_score_latency")),

        "dataset_quality": safe_score(scores.get("dataset_quality")),
        "dataset_quality_latency": safe_latency(scores.get("dataset_quality_latency")),

        "code_quality": safe_score(scores.get("code_quality")),
        "code_quality_latency": safe_latency(scores.get("code_quality_latency")),
    }


def score_repo_from_owner_and_repo(owner: str, repo: str) -> Dict[str, float]:
    log.info("Scoring repository %s/%s", owner, repo)
    api_data = fetch_repo_data(owner=owner, repo=repo)
    return net_score(api_data)


def score_dataset_from_id(dataset_id: str) -> Dict[str, float]:
    """Score a Hugging Face dataset using available metrics."""
    api_data = fetch_dataset_data(dataset_id)

    model_data = {
        "repo_size_bytes": 0,
        "license": api_data.get("license"),
        "readme": api_data.get("readme", ""),
        "maintainers": [api_data.get("author")],
        "has_code": False,
        "has_dataset": True,
    }

    size_scores = {
        "raspberry_pi": 0.5,
        "jetson_nano": 0.5,
        "desktop_pc": 0.5,
        "aws_server": 0.5,
    }

    size_score_avg = 0.5
    size_latency = 0  # Default latency for static dataset scores

    license_score, license_latency = score_license_with_latency(model_data)
    ramp_up_score, ramp_up_latency = score_ramp_up_time_with_latency(model_data["readme"])
    bus_factor_score, bus_factor_latency = score_bus_factor_with_latency(model_data["maintainers"])
    availability_score, availability_latency = score_available_dataset_and_code_with_latency(
        model_data["has_code"], model_data["has_dataset"]
    )
    dataset_quality_score, dataset_quality_latency = score_dataset_quality_with_latency(api_data)
    performance_claims_score, performance_claims_latency = score_performance_claims_with_latency(model_data)

    scores = {
        "size": size_scores,
        "size_score": size_score_avg,
        "size_score_latency": size_latency,

        "license": license_score,
        "license_latency": license_latency,

        "ramp_up_time": ramp_up_score,
        "ramp_up_time_latency": ramp_up_latency,

        "bus_factor": bus_factor_score,
        "bus_factor_latency": bus_factor_latency,

        "dataset_and_code_score": availability_score,
        "dataset_and_code_score_latency": availability_latency,

        "dataset_quality": dataset_quality_score,
        "dataset_quality_latency": dataset_quality_latency,

        "code_quality": 0.0,
        "code_quality_latency": 0,

        "performance_claims": performance_claims_score,
        "performance_claims_latency": performance_claims_latency,
    }

    weights = {
        "size_score": 0.1,
        "license": 0.15,
        "ramp_up_time": 0.15,
        "bus_factor": 0.1,
        "dataset_and_code_score": 0.1,
        "dataset_quality": 0.2,
        "code_quality": 0.0,
        "performance_claims": 0.2,
    }

    netscore = sum(scores[k] * weights[k] for k in weights)
    scores["net_score"] = round(netscore, 3)

    scores["net_score_latency"] = (
        size_latency + license_latency + ramp_up_latency + bus_factor_latency +
        availability_latency + dataset_quality_latency +
        0 +  # code_quality_latency
        performance_claims_latency
    )

    return scores
