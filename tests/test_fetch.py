from unittest.mock import MagicMock, patch

from ai_model_catalog.fetch_repo import (
    SAMPLE_ACTION_RUN,
    fetch_hf_model,
    fetch_repo_data,
)


# --- Helpers to fake requests.get ---
def fake_response(json_data, status=200, text_data=None, headers=None):
    mock_resp = MagicMock()
    mock_resp.status_code = status
    mock_resp.json.return_value = json_data
    mock_resp.text = text_data or ""
    mock_resp.headers = headers or {}
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


# --- Tests ---
@patch("requests.get")
def test_fetch_repo_data(mock_get):
    # Fake /repos/{owner}/{repo}
    repo_json = {
        "full_name": "huggingface/transformers",
        "size": 12345,
        "license": {"spdx_id": "Apache-2.0"},
        "owner": {"login": "huggingface"},
        "stargazers_count": 1337,
        "forks_count": 42,
        "open_issues_count": 7,
        "updated_at": "2025-09-16T00:00:00Z",
    }

    # Fake /repos/{owner}/{repo}/readme
    readme_json = {"download_url": "https://fakeurl/readme.md"}
    readme_text = "# Transformers README"

    # Fake /repos/{owner}/{repo}/commits
    commits_json = [{"sha": "abc123", "commit": {"message": "Test commit"}}]

    # Fake /repos/{owner}/{repo}/contributors
    contributors_json = [{"login": "user1", "contributions": 100}]

    # Fake /repos/{owner}/{repo}/issues
    issues_json = [{"number": 1, "title": "Test issue"}]

    # Fake /repos/{owner}/{repo}/pulls
    pulls_json = [{"number": 1, "title": "Test PR"}]

    # Fake /repos/{owner}/{repo}/actions/runs
    actions_json = {"workflow_runs": [SAMPLE_ACTION_RUN]}

    # Configure side effects for sequential calls
    mock_get.side_effect = [
        fake_response(repo_json),  # repo (rate limit check)
        fake_response(readme_json, status=200),  # readme metadata
        fake_response(text_data=readme_text, json_data={}),  # readme content download
        # Count fetching calls (per_page=1) with Link headers
        fake_response(
            commits_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/test/commits?per_page=1&page=100>; "
                    'rel="last"'
                )
            },
        ),  # commits count
        fake_response(
            contributors_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/test/contributors?per_page=1&page=50>; "
                    'rel="last"'
                )
            },
        ),  # contributors count
        fake_response(
            issues_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/test/issues?per_page=1&page=25>; "
                    'rel="last"'
                )
            },
        ),  # issues count
        fake_response(
            pulls_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/test/pulls?per_page=1&page=75>; "
                    'rel="last"'
                )
            },
        ),  # pulls count
        fake_response(
            actions_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/test/actions/runs?per_page=1&page=200>; "
                    'rel="last"'
                )
            },
        ),  # actions count
        # Sample data calls (per_page=5)
        fake_response(commits_json),  # commits sample
        fake_response(contributors_json),  # contributors sample
        fake_response(issues_json),  # issues sample
        fake_response(pulls_json),  # pulls sample
        fake_response(actions_json),  # actions sample
    ]

    data = fetch_repo_data("huggingface", "transformers")

    assert data["full_name"] == "huggingface/transformers"
    assert data["license"]["spdx_id"] == "Apache-2.0"
    assert data["stars"] == 1337
    assert data["forks"] == 42
    assert data["open_issues"] == 7
    assert "Transformers README" in data["readme"]
    assert data["actions"][0]["conclusion"] == "success"
    # Test count fields
    assert data["commits_count"] == 100
    assert data["contributors_count"] == 50
    assert data["issues_count"] == 25
    assert data["pulls_count"] == 75
    assert data["actions_count"] == 200


@patch("requests.get")
def test_fetch_hf_model(mock_get):
    model_json = {
        "usedStorage": 54321,
        "license": "apache-2.0",
        "author": "huggingface",
        "cardData": {"content": "This is the model card"},
        "downloads": 9999,
        "lastModified": "2025-09-15T12:34:56Z",
    }

    mock_get.return_value = fake_response(model_json)

    data = fetch_hf_model("bert-base-uncased")

    assert data["modelSize"] == 54321
    assert data["license"] == "apache-2.0"
    assert data["author"] == "huggingface"
    assert "model card" in data["readme"]
    assert data["downloads"] == 9999
    assert data["lastModified"].startswith("2025-09-15")
