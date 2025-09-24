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
    assert isinstance(scores["size"], dict)
    assert "raspberry_pi" in scores["size"]
    assert "jetson_nano" in scores["size"]
    assert "desktop_pc" in scores["size"]
    assert "aws_server" in scores["size"]
    # Size score average should be around 0.95
    assert 0.9 <= scores["size_score"] <= 1.0

    assert scores["license"] == 1.0
    assert scores["ramp_up_time"] == 1.0  # README >= 250 chars
    assert scores["bus_factor"] == 1.0
    assert scores["availability"] == 1.0  # defaults True/True
    assert scores["dataset_quality"] == 1.0  # word + known name + link + tag
    assert scores["code_quality"] == 1.0  # tests + CI + lint + typing/docs
    assert scores["performance_claims"] == 1.0

    # NetScore should be high due to good scores
    assert scores["NetScore"] >= 0.9


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
    assert isinstance(scores["size"], dict)
    assert "raspberry_pi" in scores["size"]
    assert "jetson_nano" in scores["size"]
    assert "desktop_pc" in scores["size"]
    assert "aws_server" in scores["size"]
    # Size score average should be around 0.95 for 50MB
    assert 0.9 <= scores["size_score"] <= 1.0

    assert scores["license"] == 0.0
    assert scores["ramp_up_time"] == 0.0
    assert scores["bus_factor"] == 1.0
    assert scores["availability"] == 1.0
    assert scores["dataset_quality"] == 0.0
    assert scores["code_quality"] == 0.0
    assert scores["performance_claims"] == 0.0

    # NetScore should be moderate due to mixed scores
    assert 0.2 <= scores["NetScore"] <= 0.4
