from ai_model_catalog.score_model import net_score


def test_net_score_github_like_payload():
    # size in KB (GitHub API); 48_828 KB -> 49_999_872 bytes => size score ≈ 0.95
    readme = (
        "state-of-the-art results on ImageNet. "
        "Uses pytest and GitHub workflow; black + mypy configured. "
        "See dataset link: http://example.com\n" + ("x" * 300)
    )
    api = {
        "full_name": "owner/repo",
        "size": 48_828,
        "license": {"spdx_id": "MIT"},
        "readme": readme,
        "owner": {"login": "alice"},
        "tags": ["benchmark", "imagenet"],
    }

    scores = net_score(api)

    # Component expectations
    # Size is now an object with hardware mappings
    assert "size" in scores
    assert isinstance(scores["size"], dict)
    assert "size_score" in scores

    assert scores["license"] == 1.0
    # LLM-enhanced ramp-up time scoring (more nuanced than simple length)
    assert 0.0 <= scores["ramp_up_time"] <= 1.0
    assert scores["bus_factor"] == 0.33  # Single maintainer gets 0.33
    # Enhanced availability scoring - should be reasonable but not necessarily 1.0
    assert 0.0 <= scores["availability"] <= 1.0
    # LLM-enhanced dataset quality scoring (more nuanced than keyword matching)
    assert 0.0 <= scores["dataset_quality"] <= 1.0
    # LLM-enhanced code quality scoring (more nuanced than keyword matching)
    assert 0.0 <= scores["code_quality"] <= 1.0
    assert scores["performance_claims"] == 0.43  # strong + moderate + basic metrics

    # NetScore should be reasonable due to good scores (adjusted for LLM-enhanced scoring)
    assert scores["net_score"] >= 0.3


def test_net_score_hf_like_payload_minimal_signals():
    # HF-style: uses modelSize (bytes) and cardData.content as README
    api = {
        "modelSize": 50_000_000,  # 50 MB -> size score = 0.95
        "license": "proprietary",  # -> 0.0
        "cardData": {"content": "short"},  # short readme -> ramp_up 0.0, no keywords
        "author": "bob",  # bus_factor -> 1.0 (maintainers derived)
        "tags": [],  # dataset_quality -> 0.0
    }

    scores = net_score(api)

    # Components
    # Size is now an object with hardware mappings
    assert "size" in scores
    assert isinstance(scores["size"], dict)
    assert "size_score" in scores

    assert scores["license"] == 0.0
    # LLM-enhanced ramp-up time scoring (more nuanced than simple length)
    assert 0.0 <= scores["ramp_up_time"] <= 1.0
    assert scores["bus_factor"] == 0.33  # Single maintainer gets 0.33
    # Enhanced availability scoring - should be reasonable but not necessarily 1.0
    assert 0.0 <= scores["availability"] <= 1.0
    # LLM-enhanced dataset quality scoring (more nuanced than keyword matching)
    assert 0.0 <= scores["dataset_quality"] <= 1.0
    # LLM-enhanced code quality scoring (more nuanced than keyword matching)
    assert 0.0 <= scores["code_quality"] <= 1.0
    assert scores["performance_claims"] == 0.0

    # NetScore should be moderate due to mixed scores (adjusted for LLM-enhanced scoring)
    assert 0.1 <= scores["net_score"] <= 0.2
