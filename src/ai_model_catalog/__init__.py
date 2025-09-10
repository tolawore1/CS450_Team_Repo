"""
AI Model Catalog - Interactive CLI for browsing AI/ML models
"""
import typer
from .cli import models, hf_model

def main():
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
                models(owner=owner, repo=repo)

            elif choice == "2":
                print("\n🤗 Hugging Face Model Search")
                model_id = (input("Enter model ID (default: bert-base-uncased): ")
                           .strip() or "bert-base-uncased")
                print(f"\nFetching data for model: {model_id}...")
                hf_model(model_id=model_id)

            elif choice == "3":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue

            # Ask if user wants to continue
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

# This will run when the module is imported
def run_interactive():
    """Run the interactive CLI when imported."""
    main()

# This will run when the module is executed directly
if __name__ == "__main__":
    main()
