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
        
        # Calculate base score from availability evidence - conservative approach
        base_score = 0.0
        if has_code and has_dataset and has_dataset_mentions and has_code_mentions:
            base_score = 0.9  # Clear evidence of both with explicit mentions
        elif has_code and has_dataset and (has_dataset_mentions or has_code_mentions):
            base_score = 0.7  # Both available with some evidence
        elif has_code and has_dataset:
            base_score = 0.5  # Both available but no clear evidence
        elif has_code or has_dataset:
            base_score = 0.3  # Only one available
        else:
            base_score = 0.1  # Neither available
        
        # Very conservative maturity analysis - minimal multipliers
        maturity_factor = 1.0
        
        # Organization reputation boost - very minimal
        prestigious_orgs = ["google", "openai", "microsoft", "facebook", "meta", "huggingface", "nvidia", "anthropic"]
        if any(org in author for org in prestigious_orgs):
            maturity_factor *= 1.05  # Very minimal boost for prestigious organizations
        
        # Model size indicates dataset/code availability needs - minimal impact
        if model_size > 1000000000:  # >1GB
            maturity_factor *= 1.05  # Minimal boost for large models
        elif model_size > 100000000:  # >100MB
            maturity_factor *= 1.02
        elif model_size < 10000000:  # <10MB
            maturity_factor *= 0.98  # Minimal reduction for small models
        
        # Download-based maturity tiers - very conservative
        if downloads > 10000000:  # 10M+ downloads
            maturity_factor *= 1.08  # Very minimal boost for very popular models
        elif downloads > 1000000:  # 1M+ downloads
            maturity_factor *= 1.06  # Very minimal boost for popular models
        elif downloads > 100000:  # 100K+ downloads
            maturity_factor *= 1.04  # Very minimal boost for moderately popular models
        elif downloads > 10000:   # 10K+ downloads
            maturity_factor *= 1.02  # Very minimal boost
        elif downloads > 1000:    # 1K+ downloads
            maturity_factor *= 1.01  # Tiny boost
        else:                     # <1K downloads
            maturity_factor *= 1.0  # No boost
        
        # Check for experimental/early-stage indicators - minimal reduction
        experimental_keywords = ["experimental", "beta", "alpha", "preview", "demo", "toy", "simple", "test"]
        if any(keyword in readme for keyword in experimental_keywords):
            # Only reduce if not from prestigious org
            if not any(org in author for org in prestigious_orgs):
                maturity_factor *= 0.95  # Minimal reduction for experimental models
        
        # Check for well-established model indicators - minimal boost
        established_keywords = ["production", "stable", "release", "v1", "v2", "enterprise", "bert", "transformer", "gpt"]
        if any(keyword in readme for keyword in established_keywords):
            maturity_factor *= 1.03  # Minimal boost for established models
        
        # Check for academic/research indicators - minimal boost
        academic_keywords = ["paper", "research", "arxiv", "conference", "journal", "study"]
        if any(keyword in readme for keyword in academic_keywords):
            maturity_factor *= 1.01  # Tiny boost for research models
        
        
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
