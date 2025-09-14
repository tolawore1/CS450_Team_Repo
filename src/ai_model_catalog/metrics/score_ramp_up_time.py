def score_ramp_up_time(readme_text: str) -> float:
    if readme_text and len(readme_text) >= 250:
        return 1.0
    else:
        return 0.0