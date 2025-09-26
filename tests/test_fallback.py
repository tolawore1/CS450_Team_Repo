#!/usr/bin/env python3
"""
Test LLM fallback behavior when API key is not set.
Run with: python test_fallback.py
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_fallback_behavior():
    """Test that fallback methods work when LLM key is not set."""
    print("🔍 Testing LLM Fallback Behavior")
    print("=" * 40)

    # Ensure no LLM key is set
    if "GEN_AI_STUDIO_API_KEY" in os.environ:
        del os.environ["GEN_AI_STUDIO_API_KEY"]

    print("✅ GEN_AI_STUDIO_API_KEY not set (as expected)")

    try:
        from ai_model_catalog.score_model import score_model_from_id

        model_id = "google-bert/bert-base-uncased"
        print(f"\n📊 Testing model scoring for: {model_id}")

        # Test the scoring
        result = score_model_from_id(model_id)

        print("\n📈 Scoring Results:")
        print(f"  Net Score: {result.get('NetScore', 'N/A')}")
        print(f"  License: {result.get('license', 'N/A')}")
        print(f"  Ramp Up Time: {result.get('ramp_up_time', 'N/A')}")
        print(f"  Bus Factor: {result.get('bus_factor', 'N/A')}")
        print(f"  Code Quality: {result.get('code_quality', 'N/A')}")
        print(f"  Dataset Quality: {result.get('dataset_quality', 'N/A')}")
        print(f"  Performance Claims: {result.get('performance_claims', 'N/A')}")

        # Check if we got reasonable values (not just -1)
        non_negative_scores = [
            k for k, v in result.items() if isinstance(v, (int, float)) and v >= 0
        ]
        print(f"\n✅ Non-negative scores: {len(non_negative_scores)}/{len(result)}")

        if len(non_negative_scores) > 0:
            print("✅ Fallback methods are working correctly!")
            return True
        print("❌ All scores are -1, fallback may not be working")
        return False

    except (ImportError, AttributeError, KeyError, ValueError) as e:
        print(f"❌ Error testing fallback: {e}")
        return False


def test_individual_metrics():
    """Test individual metric functions."""
    print("\n🔧 Testing Individual Metrics")
    print("=" * 40)

    try:
        from ai_model_catalog.metrics import (
            score_ramp_up_time,
            score_code_quality,
            score_dataset_quality,
        )

        # Test data
        test_data = {
            "readme": "# Test Model\n\nThis is a test model with installation instructions.",
            "cardData": {
                "content": "# Test Model\n\nThis is a test model with installation instructions."
            },
        }

        print("Testing ramp_up_time...")
        ramp_score = score_ramp_up_time(test_data)
        print(f"  Ramp Up Time Score: {ramp_score}")

        print("Testing code_quality...")
        code_score = score_code_quality(test_data)
        print(f"  Code Quality Score: {code_score}")

        print("Testing dataset_quality...")
        dataset_score = score_dataset_quality(test_data)
        print(f"  Dataset Quality Score: {dataset_score}")

        # Check if we got reasonable values
        scores = [ramp_score, code_score, dataset_score]
        valid_scores = [s for s in scores if isinstance(s, (int, float)) and s >= 0]

        print(f"\n✅ Valid scores: {len(valid_scores)}/{len(scores)}")

        if len(valid_scores) > 0:
            print("✅ Individual metrics are working with fallback!")
            return True
        print("❌ Individual metrics may not be using fallback correctly")
        return False

    except (ImportError, AttributeError, KeyError, ValueError) as e:
        print(f"❌ Error testing individual metrics: {e}")
        return False


def main():
    """Run all fallback tests."""
    print("🧪 LLM Fallback Test Suite")
    print("=" * 50)

    # Test 1: Overall scoring behavior
    fallback_works = test_fallback_behavior()

    # Test 2: Individual metrics
    individual_works = test_individual_metrics()

    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"  Overall Fallback: {'✅ PASS' if fallback_works else '❌ FAIL'}")
    print(f"  Individual Metrics: {'✅ PASS' if individual_works else '❌ FAIL'}")

    if fallback_works and individual_works:
        print("\n🎉 All fallback tests passed! The system is working correctly.")
    else:
        print(
            "\n⚠️  Some fallback tests failed. There may be an issue with the fallback logic."
        )


if __name__ == "__main__":
    main()
