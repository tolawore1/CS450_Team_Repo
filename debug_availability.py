#!/usr/bin/env python3
"""Debug availability function call."""

import sys
import os

# Add src to path
sys.path.append("src")

# Set environment variables
os.environ["GITHUB_TOKEN"] = "test_token"

try:
    from ai_model_catalog.metrics import score_available_dataset_and_code as score_availability
    from ai_model_catalog.score_model import _time_metric
    
    print("🔍 Testing availability function...")
    
    # Test direct call
    print("Direct call:")
    result = score_availability(True, True)
    print(f"Result: {result}")
    
    # Test with _time_metric
    print("\nWith _time_metric:")
    score, latency = _time_metric(score_availability, True, True)
    print(f"Score: {score}, Latency: {latency}ms")
    
    # Test with wrong number of arguments
    print("\nWith wrong arguments:")
    try:
        score, latency = _time_metric(score_availability, True)
        print(f"Score: {score}, Latency: {latency}ms")
    except Exception as e:
        print(f"Error: {e}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
