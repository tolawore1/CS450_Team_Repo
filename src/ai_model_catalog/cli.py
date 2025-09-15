"""
AI Model Catalog - CLI for browsing AI/ML models
"""
import logging
import typer
<<<<<<< HEAD
from . import fetch_repo as fr
=======
from ai_model_catalog.metrics.score_model import netScore
>>>>>>> 5f3359fc5a24166aa30c90a29e31e37ce9a809de

app = typer.Typer(help="AI/ML model catalog CLI")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("catalog")

# --- GitHub repo command ---
@app.command()
def models(owner: str = "huggingface", repo: str = "transformers"):
    """Fetch metadata from GitHub API for a repo."""
<<<<<<< HEAD
    fr.models(owner=owner, repo=repo)
=======
    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    log.info("Repo: %s ⭐ %s", data["full_name"], data["stargazers_count"])
    typer.echo(data.get("description", ""))
    scores = netScore(data)
    typer.echo("\nNetScore Breakdown:")
    for k, v in scores.items():
        typer.echo(f"{k}: {v}")
>>>>>>> 5f3359fc5a24166aa30c90a29e31e37ce9a809de

# --- Hugging Face model command ---
@app.command()
def hf_model(model_id: str = "bert-base-uncased"):
    """Fetch metadata from Hugging Face Hub for a given model ID."""
    fr.hf_model(model_id=model_id)

<<<<<<< HEAD
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
                owner = (input("Enter repository owner (default: huggingface): ")
                        .strip() or "huggingface")
                repo = (input("Enter repository name (default: transformers): ")
                       .strip() or "transformers")
                print(f"\nFetching data for {owner}/{repo}...")
                fr.models(owner=owner, repo=repo)

            elif choice == "2":
                print("\n🤗 Hugging Face Model Search")
                model_id = (input("Enter model ID (default: bert-base-uncased): ")
                           .strip() or "bert-base-uncased")
                print(f"\nFetching data for model: {model_id}...")
                fr.hf_model(model_id=model_id)

            elif choice == "3":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue

            continue_choice = (input("\nWould you like to explore another model? (y/n): ")
                              .strip().lower())
            if continue_choice not in ['y', 'yes']:
                print("👋 Goodbye!")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except (ValueError, ConnectionError, TimeoutError) as e:
            print(f"❌ An error occurred: {e}")
            continue
=======
    typer.echo(f"Model: {data['modelId']}")
    typer.echo(f"Last Modified: {data['lastModified']}")
    typer.echo(f"Downloads: {data.get('downloads', 'N/A')}")
    typer.echo(f"Tags: {', '.join(data.get('tags', []))}")
    if "pipeline_tag" in data:
        typer.echo(f"Task: {data['pipeline_tag']}")
        
    scores = netScore(data)
    typer.echo("\nNetScore Breakdown:")
    for k, v in scores.items():
        typer.echo(f"{k}: {v}")
>>>>>>> 5f3359fc5a24166aa30c90a29e31e37ce9a809de

if __name__ == "__main__":
    app(prog_name="cli.py")
