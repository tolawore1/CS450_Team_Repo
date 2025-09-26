#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_model_catalog.fetch_repo import fetch_model_data
from ai_model_catalog.metrics.score_performance_claims import score_performance_claims

def debug_run_data():
    print("=== DEBUGGING RUN FILE DATA STRUCTURE ===")
    
    # Simulate what the run file does
    api_data = fetch_model_data("audience_classifier_model")
    readme = api_data.get("readme", "") or api_data.get("cardData", {}).get("content", "")
    maintainers = [api_data.get("author")]
    model_data = {
        "repo_size_bytes": api_data.get("modelSize", 0),
        "license": api_data.get("license"),
        "readme": readme,
        "maintainers": maintainers,
        "has_code": True,
        "has_dataset": True,
    }
    
    print("Model data keys:", list(model_data.keys()))
    print("Model data name field:", model_data.get("name", "MISSING"))
    print("Readme content:", repr(readme))
    
    # Test performance claims
    score = score_performance_claims(model_data)
    print("Performance claims score:", score)

if __name__ == "__main__":
    debug_run_data()
