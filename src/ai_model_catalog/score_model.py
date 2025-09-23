import logging
from typing import Dict

from .metrics.score_available_dataset_and_code import (
    score_available_dataset_and_code as score_availability,
)
from .fetch_repo import fetch_model_data
from .fetch_repo import fetch_repo_data
from .metrics.score_bus_factor import score_bus_factor
from .metrics.score_code_quality import score_code_quality
from .metrics.score_dataset_quality import score_dataset_quality
from .metrics.score_license import score_license
from .metrics.score_performance_claims import score_performance_claims
from .metrics.score_ramp_up_time import score_ramp_up_time
from .metrics.score_size import score_size

log = logging.getLogger(__name__)


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

    scores = {
        "size": score_size(model_data["repo_size_bytes"]),
        "license": score_license(model_data["license"]),
        "ramp_up_time": score_ramp_up_time(model_data["readme"]),
        "bus_factor": score_bus_factor(model_data["maintainers"]),
        "availability": score_availability(
            model_data["has_code"], model_data["has_dataset"]
        ),
        "dataset_quality": score_dataset_quality(api_data),
        "code_quality": score_code_quality(api_data),
        "performance_claims": score_performance_claims(model_data["readme"]),
    }

    weights = {
        "size": 0.1,
        "license": 0.15,
        "ramp_up_time": 0.15,
        "bus_factor": 0.1,
        "availability": 0.1,
        "dataset_quality": 0.1,
        "code_quality": 0.15,
        "performance_claims": 0.15,
    }

    netscore = sum(scores[k] * weights[k] for k in scores)
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
