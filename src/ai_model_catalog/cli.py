"""AI Model Catalog - CLI for browsing AI/ML models"""

import logging
from typing import Dict, Any
import typer
from ai_model_catalog.score_model import net_score
from . import fetch_repo as fr
from .fetch_repo import GitHubAPIError, RepositoryDataError

app = typer.Typer(help="AI/ML model catalog CLI")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("catalog")


def _format_repository_data(
    data: Dict[str, Any], owner: str, repo: str
) -> Dict[str, Any]:
    """Extract and format repository data for display."""
    return {
        "full_name": data.get("full_name") or f"{owner}/{repo}",
        "stars": data.get("stargazers_count")
        or data.get("stargazers")
        or data.get("stars")
        or 0,
        "forks": data.get("forks_count") or data.get("forks") or 0,
        "language": data.get("language") or data.get("primary_language") or "N/A",
        "updated": data.get("pushed_at")
        or data.get("updated_at")
        or data.get("lastModified")
        or "N/A",
        "open_issues": data.get("open_issues_count") or data.get("open_issues") or 0,
        "size": data.get("size", 0),
        "license_name": _extract_license_name(data.get("license", {})),
        "description": data.get("description") or "No description available",
        "default_branch": data.get("default_branch", "main"),
        "readme": data.get("readme", ""),
    }


def _extract_license_name(license_info: Any) -> str:
    """Extract license name from license info."""
    if isinstance(license_info, dict):
        return license_info.get("spdx_id") or "None"
    return license_info or "None"


def _format_count_info(data: Dict[str, Any], key: str, display_name: str) -> str:
    """Format count information with fallback to sample data."""
    count = data.get(f"{key}_count", 0)
    sample_data = data.get(key, [])

    if count == 0:
        sample_count = len(sample_data)
        return f"Recent {display_name}: {sample_count} (showing first 30)"
    return f"Total {display_name}: {count:,}"


def _display_repository_info(
    formatted_data: Dict[str, Any], counts_info: Dict[str, str]
) -> None:
    """Display formatted repository information."""
    log.info("Repo: %s ⭐ %s", formatted_data["full_name"], formatted_data["stars"])

    typer.echo(f"Description: {formatted_data['description']}")
    typer.echo(f"Default branch: {formatted_data['default_branch']}")
    typer.echo(f"Language: {formatted_data['language']}")
    typer.echo(f"Updated: {formatted_data['updated']}")
    typer.echo(f"Stars: {formatted_data['stars']:,}")
    typer.echo(f"Forks: {formatted_data['forks']:,}")
    typer.echo(f"Open issues: {formatted_data['open_issues']}")
    typer.echo(f"Size: {formatted_data['size']:,} KB")
    typer.echo(f"License: {formatted_data['license_name']}")
    typer.echo(counts_info["commits"])
    typer.echo(counts_info["contributors"])
    typer.echo(counts_info["issues"])
    typer.echo(counts_info["pulls"])
    typer.echo(counts_info["actions"])
    typer.echo(f"README length: {len(formatted_data['readme'])} characters")


def _display_scores(data: Dict[str, Any]) -> None:
    """Display NetScore breakdown."""
    scores = net_score(data)
    typer.echo("\nNetScore Breakdown:")
    for key, value in scores.items():
        typer.echo(f"{key}: {value:.3f}")


def _format_model_data(data: Dict[str, Any], model_id: str) -> Dict[str, Any]:
    """Extract and format model data for display."""
    return {
        "model_name": data.get("modelId", model_id),
        "author": data.get("author", "Unknown"),
        "description": data.get("description", ""),
        "model_size": data.get("modelSize", 0),
        "downloads": data.get("downloads", 0),
        "last_modified": data.get("lastModified", "Unknown"),
        "readme": data.get("readme", ""),
        "license_name": _extract_license_name(data.get("license")),
        "tags": data.get("tags") or [],
        "task": data.get("pipeline_tag"),
    }


def _display_model_info(formatted_data: Dict[str, Any]) -> None:
    """Display formatted model information."""
    typer.echo(f"Model: {formatted_data['model_name']}")
    typer.echo(f"Author: {formatted_data['author']}")
    typer.echo(
        f"Description: {formatted_data['description'] or 'No description available'}"
    )
    typer.echo(f"Model Size: {formatted_data['model_size']:,} bytes")
    typer.echo(f"License: {formatted_data['license_name']}")
    typer.echo(f"Downloads: {formatted_data['downloads']:,}")
    typer.echo(f"Last Modified: {formatted_data['last_modified']}")
    typer.echo(f"README length: {len(formatted_data['readme'])} characters")

    if isinstance(formatted_data["tags"], list) and formatted_data["tags"]:
        typer.echo(f"Tags: {', '.join(formatted_data['tags'])}")
    if formatted_data["task"]:
        typer.echo(f"Task: {formatted_data['task']}")


def _get_repository_counts_info(data: Dict[str, Any]) -> Dict[str, str]:
    """Get formatted count information for repository data."""
    return {
        "commits": _format_count_info(data, "commits", "commits"),
        "contributors": _format_count_info(data, "contributors", "contributors"),
        "issues": _format_count_info(data, "issues", "issues"),
        "pulls": _format_count_info(data, "pulls", "pull requests"),
        "actions": _format_count_info(data, "actions", "actions runs"),
    }


def _handle_repository_command(owner: str, repo: str) -> None:
    """Handle the repository command logic."""
    data = fr.fetch_repo_data(owner=owner, repo=repo)
    formatted_data = _format_repository_data(data, owner, repo)
    counts_info = _get_repository_counts_info(data)

    _display_repository_info(formatted_data, counts_info)
    _display_scores(data)


def _handle_model_command(model_id: str) -> None:
    """Handle the Hugging Face model command logic."""
    data = fr.fetch_hf_model(model_id=model_id)
    formatted_data = _format_model_data(data, model_id)

    _display_model_info(formatted_data)
    _display_scores(data)


@app.command()
def models(owner: str = "huggingface", repo: str = "transformers"):
    """Fetch metadata from GitHub API for a repo."""
    _handle_repository_command(owner, repo)


@app.command()
def hf_model(model_id: str = "bert-base-uncased"):
    """Fetch metadata from Hugging Face Hub for a given model ID."""
    _handle_model_command(model_id)


@app.command()
def interactive():
    """Start interactive mode for browsing AI models."""
    interactive_main()


def _get_user_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default value."""
    return input(f"{prompt} (default: {default}): ").strip() or default


def _display_repository_interactive(
    data: Dict[str, Any], owner: str, repo: str
) -> None:
    """Display repository information in interactive mode."""
    formatted_data = _format_repository_data(data, owner, repo)
    counts_info = _get_repository_counts_info(data)

    print("\n📊 Repository Information:")
    print(f"Name: {formatted_data['full_name']}")
    print(f"Description: {formatted_data['description']}")
    print(f"Language: {formatted_data['language']}")
    print(f"Updated: {formatted_data['updated']}")
    print(f"Stars: {formatted_data['stars']:,}")
    print(f"Forks: {formatted_data['forks']:,}")
    print(f"Open issues: {formatted_data['open_issues']}")
    print(f"Size: {formatted_data['size']:,} KB")
    print(f"License: {formatted_data['license_name']}")
    print(counts_info["commits"])
    print(counts_info["contributors"])
    print(counts_info["issues"])
    print(counts_info["pulls"])
    print(counts_info["actions"])
    print(f"README length: {len(formatted_data['readme'])} characters")

    scores = net_score(data)
    print("\n📈 NetScore Breakdown:")
    for key, value in scores.items():
        print(f"{key}: {value:.3f}")


def _display_model_interactive(data: Dict[str, Any], model_id: str) -> None:
    """Display model information in interactive mode."""
    formatted_data = _format_model_data(data, model_id)

    print("\n🤖 Model Information:")
    print(f"Model: {formatted_data['model_name']}")
    print(f"Author: {formatted_data['author']}")
    print(f"Description: {formatted_data['description'] or 'No description available'}")
    print(f"Model Size: {formatted_data['model_size']:,} bytes")
    print(f"License: {formatted_data['license_name']}")
    print(f"Downloads: {formatted_data['downloads']:,}")
    print(f"Last Modified: {formatted_data['last_modified']}")
    print(f"README length: {len(formatted_data['readme'])} characters")

    if isinstance(formatted_data["tags"], list) and formatted_data["tags"]:
        print(f"Tags: {', '.join(formatted_data['tags'])}")
    if formatted_data["task"]:
        print(f"Task: {formatted_data['task']}")

    scores = net_score(data)
    print("\n📈 NetScore Breakdown:")
    for key, value in scores.items():
        print(f"{key}: {value:.3f}")


def _handle_github_repository_interactive() -> None:
    """Handle GitHub repository browsing in interactive mode."""
    print("\n📁 GitHub Repository Browser")

    # Display available owners
    _display_available_owners()

    # Get owner selection as integer
    while True:
        try:
            owner_choice = int(input("Select repository owner (1-5): ").strip())
            if 1 <= owner_choice <= 5:
                break
            print("❌ Please enter a number between 1 and 5.")
        except ValueError:
            print("❌ Please enter a valid number.")

    # Map choice to owner name
    owners = [
        "huggingface",
        "openai",
        "facebookresearch",
        "google-research",
        "microsoft",
    ]
    owner = owners[owner_choice - 1]

    # Display repositories for the selected owner
    _display_owner_repositories(owner_choice)
    repo = _get_user_input("Enter repository name", "transformers")

    print(f"\nFetching data for {owner}/{repo}...")
    try:
        data = fr.fetch_repo_data(owner=owner, repo=repo)
        _display_repository_interactive(data, owner, repo)
    except (GitHubAPIError, RepositoryDataError) as e:
        print(f"❌ Error fetching repository data: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
    except (ValueError, ConnectionError, TimeoutError) as e:
        print(f"❌ Network or data error: {e}")


def _handle_huggingface_model_interactive() -> None:
    """Handle Hugging Face model search in interactive mode."""
    print("\n🤗 Hugging Face Model Search")
    model_id = _get_user_input("Enter model ID", "bert-base-uncased")

    print(f"\nFetching data for model: {model_id}...")
    try:
        data = fr.fetch_hf_model(model_id=model_id)
        _display_model_interactive(data, model_id)
    except (GitHubAPIError, RepositoryDataError) as e:
        print(f"❌ Error fetching model data: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
    except (ValueError, ConnectionError, TimeoutError) as e:
        print(f"❌ Network or data error: {e}")


def _display_main_menu() -> None:
    """Display the main menu options."""
    print("🤖 Welcome to AI Model Catalog!")
    print("Choose an option to explore AI models:")
    print("1. Browse GitHub repositories")
    print("2. Search Hugging Face models")
    print("3. Exit")


def _get_user_choice() -> str:
    """Get user choice from main menu."""
    return input("\nEnter your choice (1-3): ").strip()


def _should_continue() -> bool:
    """Ask user if they want to continue."""
    continue_choice = (
        input("\nWould you like to explore another model? (y/n): ").strip().lower()
    )
    return continue_choice in ["y", "yes"]


def _display_available_owners() -> None:
    """Display the list of available repository owners."""
    print("\n📋 Available Repository Owners:")
    print("1. huggingface")
    print("2. openai")
    print("3. facebookresearch (Meta AI)")
    print("4. google-research")
    print("5. microsoft")
    print()


def _display_owner_repositories(owner_choice: int) -> None:
    """Display the repositories available for a given owner choice (1-5)."""
    owners = [
        "huggingface",
        "openai",
        "facebookresearch",
        "google-research",
        "microsoft",
    ]

    repositories = {
        "huggingface": [
            "transformers → NLP, multimodal models",
            "diffusers → diffusion models (Stable Diffusion)",
            "accelerate → training large models efficiently",
            "datasets → dataset loading/sharing",
            "trl → reinforcement learning with transformers",
        ],
        "openai": [
            "openai-cookbook → practical examples & guides",
            "whisper → speech-to-text model",
            "gym → RL environments",
            "baselines → RL reference implementations",
            "microscope → visualizing neural networks",
        ],
        "facebookresearch": [
            "fairseq → sequence-to-sequence modeling",
            "llama → LLaMA language models",
            "detectron2 → object detection / vision",
            "pytorch3d → 3D deep learning",
            "esm → protein language models",
        ],
        "google-research": [
            "bert → original BERT repo",
            "t5x → T5 training framework",
            "vision_transformer → ViT models",
            "biggan → generative adversarial networks",
            "scenic → computer vision research framework",
        ],
        "microsoft": [
            "DeepSpeed → large-scale model training optimization",
            "LoRA → low-rank adaptation for large models",
            "onnxruntime → ONNX inference engine",
            "lightgbm → gradient boosting framework",
            "NCCL (in collaboration) → distributed GPU communication",
        ],
    }

    if 1 <= owner_choice <= 5:
        owner = owners[owner_choice - 1]
        print(f"\n📁 Available repositories for {owner}:")
        for i, repo in enumerate(repositories[owner], 1):
            print(f"{i}. {repo}")
        print()
    else:
        print(f"\n❌ Invalid owner choice: {owner_choice}")
        print("Please select a number between 1 and 5.")
        print()


def interactive_main():
    """Interactive main function that prompts user to select an AI model and runs CLI."""
    _display_main_menu()

    while True:
        try:
            choice = _get_user_choice()

            if choice == "1":
                _handle_github_repository_interactive()
            elif choice == "2":
                _handle_huggingface_model_interactive()
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue

            if not _should_continue():
                print("👋 Goodbye!")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(f"❌ An error occurred: {e}")
            continue


if __name__ == "__main__":
    app(prog_name="cli.py")
