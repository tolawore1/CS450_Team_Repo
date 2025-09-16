"""
Entry point for running the package as a module: python -m src.ai_model_catalog
"""

from .cli import interactive_main

if __name__ == "__main__":
    interactive_main()
