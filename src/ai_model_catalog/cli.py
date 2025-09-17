"""AI Model Catalog - CLI for browsing AI/ML models"""

import logging
import typer
from ai_model_catalog.score_model import net_score
from . import fetch_repo as fr

app = typer.Typer(help="AI/ML model catalog CLI")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("catalog")


# --- GitHub repo command ---
@app.command()
def models(owner: str = "huggingface", repo: str = "transformers"):
    """Fetch metadata from GitHub API for a repo."""
    data = fr.fetch_repo_data(owner=owner, repo=repo)

    full_name = data.get("full_name") or f"{owner}/{repo}"
    stars = (
        data.get("stargazers_count") or data.get("stargazers") or data.get("stars") or 0
    )
    language = data.get("language") or data.get("primary_language") or "N/A"
    updated = (
        data.get("pushed_at")
        or data.get("updated_at")
        or data.get("lastModified")
        or "N/A"
    )
    open_issues = data.get("open_issues_count") or data.get("open_issues") or 0

    log.info("Repo: %s ⭐ %s", full_name, stars)
    typer.echo(data.get("description") or "")
    typer.echo(f"Default branch: {data.get('default_branch', 'main')}")
    typer.echo(f"Language: {language}")
    typer.echo(f"Updated: {updated}")
    typer.echo(f"Open issues: {open_issues}")

    scores = net_score(data)
    typer.echo("\nNetScore Breakdown:")
    for k, v in scores.items():
        typer.echo(f"{k}: {v:.3f}")


# --- Hugging Face model command ---
@app.command()
def hf_model(model_id: str = "bert-base-uncased"):
    """Fetch metadata from Hugging Face Hub for a given model ID."""
    data = fr.fetch_hf_model(model_id=model_id)

    print("Model:", data.get("modelId", model_id))
    print("Author:", data.get("author", "Unknown"))
    print("Description:", data.get("description", ""))

    lic = data.get("license")
    lic_str = (
        (lic.get("spdx_id") or lic.get("id") or lic.get("name"))
        if isinstance(lic, dict)
        else (lic or "None")
    )
    print("License:", lic_str)

    print("Downloads:", f"{data.get('downloads', 0):,}")
    print("Last Modified:", data.get("lastModified"))
    tags = data.get("tags") or []
    if isinstance(tags, list) and tags:
        print("Tags:", ", ".join(tags))
    task = data.get("pipeline_tag")
    if task:
        print("Task:", task)


def interactive_main():
    """Interactive main function that prompts user to select an AI model and runs CLI."""
    print("🤖 Welcome to AI Model Catalog!")
    print("Choose an option to explore AI models:")
    print("1. Browse GitHub repositories (e.g., Hugging Face Transformers)")
    print("2. Search Hugging Face models")
    print("3. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1":
                print("\n📁 GitHub Repository Browser")
                owner = (
                    input("Enter repository owner (default: huggingface): ").strip()
                    or "huggingface"
                )
                repo = (
                    input("Enter repository name (default: transformers): ").strip()
                    or "transformers"
                )
                print(f"\nFetching data for {owner}/{repo}...")
                # data = fr.fetch_repo_data(owner=owner, repo=repo)

            elif choice == "2":
                print("\n🤗 Hugging Face Model Search")
                model_id = (
                    input("Enter model ID (default: bert-base-uncased): ").strip()
                    or "bert-base-uncased"
                )
                print(f"\nFetching data for model: {model_id}...")
                data = fr.fetch_hf_model(model_id=model_id)
                print(f"Model: {data.get('author', 'Unknown')}/{model_id}")
                print(f"Downloads: {data.get('downloads', 0):,}")
                print(f"Model Size: {data.get('modelSize', 0):,} bytes")

            elif choice == "3":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue

            continue_choice = (
                input("\nWould you like to explore another model? (y/n): ")
                .strip()
                .lower()
            )
            if continue_choice not in ["y", "yes"]:
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
