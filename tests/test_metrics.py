from ai_model_catalog.metrics import (
    score_size,
    score_license,
    score_ramp_up_time,
    score_bus_factor,
    score_available_dataset_and_code,
    score_dataset_quality,
    score_code_quality,
    score_performance_claims,
)

def test_metrics():
    assert callable(score_size)
    assert callable(score_license)
    assert callable(score_ramp_up_time)
    assert callable(score_bus_factor)
    assert callable(score_available_dataset_and_code)
    assert callable(score_dataset_quality)
    assert callable(score_code_quality)
    assert callable(score_performance_claims)  
