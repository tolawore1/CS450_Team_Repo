from unittest.mock import patch, MagicMock

from ai_model_catalog.fetch_repo import (
    fetch_repo_data,
    fetch_hf_model,
    SAMPLE_ACTION_RUN,
)


# --- Helpers to fake requests.get ---
def fake_response(json_data, status=200, text_data=None):
    mock_resp = MagicMock()
    mock_resp.status_code = status
    mock_resp.json.return_value = json_data
    mock_resp.text = text_data or ""
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
        fake_response(repo_json),  # repo (main data fetch)
        fake_response(readme_json),  # readme metadata
        fake_response(text_data=readme_text, json_data={}),  # readme content
        fake_response(commits_json),  # commits
        fake_response(contributors_json),  # contributors
        fake_response(issues_json),  # issues
        fake_response(pulls_json),  # pulls
        fake_response(actions_json),  # actions
    ]

    data = fetch_repo_data("huggingface", "transformers")

    assert data["full_name"] == "huggingface/transformers"
    assert data["license"]["spdx_id"] == "Apache-2.0"
    assert data["stars"] == 1337
    assert data["forks"] == 42
    assert data["open_issues"] == 7
    assert "Transformers README" in data["readme"]
    assert data["actions"][0]["conclusion"] == "success"


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
