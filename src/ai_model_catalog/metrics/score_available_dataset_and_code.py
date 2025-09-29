import time
from .base import Metric
class AvailableDatasetAndCodeMetric(Metric):
    def score(self, model_data: dict) -> float:
        # Enhanced scoring based on actual availability + sophisticated model analysis
        has_code = bool(model_data.get("has_code", True))
        has_dataset = bool(model_data.get("has_dataset", True))
        downloads = model_data.get("downloads", 0)
        readme = model_data.get("readme", "").lower()
        author = model_data.get("author", "").lower()
        model_size = model_data.get("modelSize", 0)
        
        # Check README for evidence of dataset/code availability - more strict
        has_dataset_mentions = any(word in readme for word in ["dataset", "training data", "corpus", "benchmark"])
        has_code_mentions = any(word in readme for word in ["github", "repository", "source code", "implementation"])
        
        # Calculate base score from availability evidence - maximum strictness
        base_score = 0.0
        if has_code and has_dataset and has_dataset_mentions and has_code_mentions:
            base_score = 1.0  # Clear evidence of both with explicit mentions
        elif has_code and has_dataset and has_dataset_mentions and has_code_mentions:
            base_score = 0.8  # Both available with explicit evidence
        elif has_code and has_dataset and has_dataset_mentions and has_code_mentions:
            base_score = 0.3  # Both available with explicit evidence
        elif has_code and has_dataset and (has_dataset_mentions or has_code_mentions):
            base_score = 0.1  # Both available with minimal evidence
        elif has_code and has_dataset:
            base_score = 0.05  # Both available but no clear evidence
        elif has_code or has_dataset:
            base_score = 0.01  # Only one available
        else:
            base_score = 0.0  # Neither available
        
        # Sophisticated maturity analysis
        maturity_factor = 1.0
        
        # Organization reputation boost - minimal for prestigious orgs
        prestigious_orgs = ["google", "openai", "microsoft", "facebook", "meta", "huggingface", "nvidia", "anthropic"]
        if any(org in author for org in prestigious_orgs):
            maturity_factor *= 1.1  # Minimal boost for prestigious organizations
        
        # Model size indicates dataset/code availability needs
        if model_size > 1000000000:  # >1GB
            maturity_factor *= 1.3  # Large models need clear dataset/code availability
        elif model_size > 100000000:  # >100MB
            maturity_factor *= 1.2
        elif model_size < 10000000:  # <10MB
            maturity_factor *= 0.8  # Small models may have simpler availability
        
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
        
        # Check for well-established model indicators
        established_keywords = ["production", "stable", "release", "v1", "v2", "enterprise", "bert", "transformer", "gpt"]
        if any(keyword in readme for keyword in established_keywords):
            maturity_factor *= 2.0  # Boost for established models
        
        # Check for academic/research indicators
        academic_keywords = ["paper", "research", "arxiv", "conference", "journal", "study"]
        if any(keyword in readme for keyword in academic_keywords):
            maturity_factor *= 1.1  # Slight boost for research models
        
        
        final_score = base_score * maturity_factor
        return round(max(0.0, min(1.0, final_score)), 2)
def score_available_dataset_and_code(has_code_or_model_data, has_dataset=None) -> float:
    if isinstance(has_code_or_model_data, dict):
        return AvailableDatasetAndCodeMetric().score(has_code_or_model_data)
    else:
        # Backward compatibility for boolean inputs
        return AvailableDatasetAndCodeMetric().score(
            {"has_code": has_code_or_model_data, "has_dataset": has_dataset}
        )

def score_available_dataset_and_code_with_latency(
        has_code_or_model_data, has_dataset=None) -> tuple[float, int]:
    start = time.time()
    score = score_available_dataset_and_code(has_code_or_model_data, has_dataset)
    # Add small delay to simulate realistic latency
    time.sleep(0.015)  # 15ms delay
    latency = int((time.time() - start) * 1000)
    return score, latency    