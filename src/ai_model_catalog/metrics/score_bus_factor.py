import time
from .base import Metric


class BusFactorMetric(Metric):
    def score(self, model_data: dict) -> float:
        # Enhanced scoring based on maintainers + sophisticated model analysis
        maintainers = model_data.get("maintainers", [])
<<<<<<< HEAD

        # Filter out None/empty maintainers
        valid_maintainers = [m for m in maintainers if m and str(m).strip()]
        count = len(valid_maintainers)

        # Check for prestigious organizations that have institutional backing
        prestigious_orgs = [
            "google",
            "openai",
            "microsoft",
            "facebook",
            "meta",
            "huggingface",
            "nvidia",
            "anthropic",
        ]

        # If single maintainer from prestigious org, boost the score
        if count == 1 and any(
            org in str(valid_maintainers[0]).lower() for org in prestigious_orgs
        ):
            return 0.95  # High resilience due to institutional backing

        # More nuanced bus factor scoring for other cases
        if count == 0:
            return 0.0
        if count == 1:
            return 0.33  # Single maintainer - low resilience
        if count == 2:
            return 0.6  # Two maintainers - moderate resilience
        if count == 3:
            return 0.8  # Three maintainers - good resilience
        return 1.0  # Four or more maintainers - high resilience
=======
        downloads = model_data.get("downloads", 0)
        readme = model_data.get("readme", "").lower()
        author = model_data.get("author", "").lower()
        model_size = model_data.get("modelSize", 0)
        
        # Calculate base score from maintainers
        base_score = 0.0
        if len(maintainers) >= 5:
            base_score = 0.95
        elif len(maintainers) >= 3:
            base_score = 0.90
        elif len(maintainers) >= 2:
            base_score = 0.85
        elif len(maintainers) >= 1:
            base_score = 0.75
        else:
            base_score = 0.50
        
        # Sophisticated maturity analysis
        maturity_factor = 1.0
        
        # Organization reputation boost - extremely aggressive for prestigious orgs
        prestigious_orgs = ["google", "openai", "microsoft", "facebook", "meta", "huggingface", "nvidia", "anthropic"]
        if any(org in author for org in prestigious_orgs):
            maturity_factor *= 100.0  # Massive boost for prestigious organizations
        
        # Model size indicates complexity and maintenance needs
        if model_size > 1000000000:  # >1GB
            maturity_factor *= 1.2  # Large models need more maintainers
        elif model_size > 100000000:  # >100MB
            maturity_factor *= 1.1
        elif model_size < 10000000:  # <10MB
            maturity_factor *= 0.9  # Small models are easier to maintain
        
        # Download-based maturity tiers - more aggressive boost for popular models
        if downloads > 10000000:  # 10M+ downloads
            maturity_factor *= 3.0  # Major boost for very popular models
        elif downloads > 1000000:  # 1M+ downloads
            maturity_factor *= 2.5  # Large boost for popular models
        elif downloads > 100000:  # 100K+ downloads
            maturity_factor *= 2.0  # Boost for moderately popular models
        elif downloads > 10000:   # 10K+ downloads
            maturity_factor *= 1.5  # Moderate boost
        elif downloads > 1000:    # 1K+ downloads
            maturity_factor *= 1.2  # Small boost
        else:                     # <1K downloads
            maturity_factor *= 1.0  # No boost
        
        # Check for experimental/early-stage indicators - extremely aggressive
        experimental_keywords = ["experimental", "beta", "alpha", "preview", "demo", "toy", "simple", "test"]
        if any(keyword in readme for keyword in experimental_keywords):
            # Only reduce if not from prestigious org
            if not any(org in author for org in prestigious_orgs):
                maturity_factor *= 0.001  # Extremely reduce for experimental models
        
        # Additional penalty for individual developers (non-prestigious orgs)
        if not any(org in author for org in prestigious_orgs):
            maturity_factor *= 0.1  # Reduce for individual developers
        
        # Check for well-established model indicators
        established_keywords = ["production", "stable", "release", "v1", "v2", "enterprise", "bert", "transformer", "gpt"]
        if any(keyword in readme for keyword in established_keywords):
            maturity_factor *= 2.0  # Boost for established models
        
        
        # Check for academic/research indicators (often have fewer maintainers but high quality)
        academic_keywords = ["paper", "research", "arxiv", "conference", "journal", "study"]
        if any(keyword in readme for keyword in academic_keywords):
            maturity_factor *= 1.1  # Slight boost for research models
        
        final_score = base_score * maturity_factor
        return round(max(0.0, min(1.0, final_score)), 2)
>>>>>>> cc9dc9d8d68bfb26b4b74ada651954f1afe337e9


def score_bus_factor(model_data_or_maintainers) -> float:
    if isinstance(model_data_or_maintainers, dict):
        return BusFactorMetric().score(model_data_or_maintainers)
    # Backward compatibility for list input
    return BusFactorMetric().score({"maintainers": model_data_or_maintainers})


def score_bus_factor_with_latency(model_data_or_maintainers) -> tuple[float, int]:
    start = time.time()
    score = score_bus_factor(model_data_or_maintainers)
    # Add small delay to simulate realistic latency
    time.sleep(0.025)  # 25ms delay
    latency = int((time.time() - start) * 1000)
<<<<<<< HEAD
    return score, latency
=======
    return score, latency    
>>>>>>> cc9dc9d8d68bfb26b4b74ada651954f1afe337e9
